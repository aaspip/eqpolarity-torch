#!/usr/bin/env python3
"""TexNet full-MT experimental inversion. Uses EXACT SAME LOCAL QuakeML, miniSEED,
station CSV defaults and station/pick matching functions as the supplied
07_texnet_eqpolarity_focal_mechanism script. Does NOT download waveforms:
the supplied polarity script reads pre-downloaded miniSEED. The only online
request here is optional station instrument-response metadata for physical units.

WARNING: homogeneous full-space analytic elastodynamics with PB1D effective
parameters, NOT an independent layered FK kernel or publication-validated MT.

#You need to install pyfk first

python 07_texnet_moment_tensor_pyfk.py \
  --physical-output DISP \
  --texnet-band 15-30 \
  --dt 0.5 \
  --fit-phase all \
  --fit-components 3C \
  --duration 1.0 \
  --pre 45 \
  --post 120 \
  --tensor-type deviatoric \
  --min-stations 6 \
  --min-snr 1.5 \
  --snr-noise-seconds 20 \
  --snr-signal-seconds 40 \
  --min-noise-seconds 10 \
  --station-shift-max 4 \
  --station-shift-step 0.5 \
  --station-shift-iterations 2 \
  --max-station-peak 0 \
  --output-dir texnet2022wmmd_MT_pyfk_v10 \
  --show
  
"""
from __future__ import annotations
import argparse, json, warnings, math
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt
from scipy.linalg import lstsq
from obspy import read, read_events
from obspy.geodetics import gps2dist_azimuth
from obspy.imaging.beachball import beach
from obspy.clients.fdsn import Client
from obspy.signal.rotate import rotate2zne
from obspy.core.stream import Stream
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt


PB1Dvel = """
-5.000 3.5000 2.0000  2.2650 79.0 36.0
0.0000 4.4050 2.5170  2.2650 79.0 36.0
2.0000 5.5250 3.1570  2.3620 131.0 58.0
4.0000 5.5250 3.1570  2.3620 131.0 58.0
6.0000 5.9170 3.3810  2.7850 262.0 116.0
8.0000 5.9170 3.3810  2.7850 262.0 116.0
10.0000 6.0610 3.4630  2.8210 524.0 233.0
12.0000 6.0610 3.4630  2.8210 524.0 233.0
14.0000 6.0610 3.4630  2.8210 524.0 233.0
16.0000 6.0610 3.4630  2.8500 613.0 272.0
18.0000 6.0610 3.4630  2.8500 613.0 272.0
20.0000 6.0610 3.4630  2.8600 702.0 312.0
22.0000 6.0610 3.4630  2.8600 702.0 312.0
24.0000 6.0610 3.4630  2.8600 702.0 312.0
26.0000 6.0610 3.4630  2.8200 791.0 352.0
28.0000 6.6230 3.7840  2.8200 791.0 352.0
30.0000 6.6230 3.7840  2.8200 881.0 392.0
32.0000 6.6230 3.7840  2.8200 881.0 392.0
34.0000 6.6230 3.7840  2.8200 881.0 392.0
36.0000 6.6230 3.7840  3.1400 913.0 406.0
38.0000 6.6230 3.7840  3.1400 913.0 406.0
40.0000 8.0000 4.5710  3.1400 913.0 406.0
42.0000 8.0000 4.5710  3.1400 913.0 406.0
""".strip()

# eid='texnet2020galz'
# eid='texnet2021ynzp'
eid='texnet2022wmmd'

DEFAULT_QML = Path(
    "/Users/chenyk/DATALIB/"
    "TexNet-refined-database-catalog-PSpicks-EVENTS/%s.qml"%eid
)
DEFAULT_MSEED = Path(
    "/Users/chenyk/DATALIB/"
    "TexNet-refined-database-catalog-PSpicks-WAVEFORMS/%s.mseed"%eid
)
DEFAULT_STATIONS = Path(
    "/Users/chenyk/chenyk.data2/various/cyksmall/"
    "texnet_stations_2024_0209_extra.csv"
)




@dataclass
class PObservation:
    pick_id: str
    network: str
    station: str
    location: str
    channel: str
    pick_time: object
    qml_azimuth: float
    qml_takeoff: float
    qml_distance_deg: float
    qml_time_weight: float
    manual_polarity: str


def as_float(value, default=np.nan):
    try:
        if value is None:
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def normalize_loc(loc):
    if loc is None:
        return ""
    s = str(loc).strip()
    if s.lower() in {"nan", "none", "--"}:
        return ""
    return s


def get_preferred_origin(event):
    origin = event.preferred_origin()
    if origin is not None:
        return origin
    if not event.origins:
        raise ValueError("QuakeML event contains no origin.")
    warnings.warn("No preferred origin; using the first origin.")
    return event.origins[0]


def get_preferred_magnitude(event):
    mag = event.preferred_magnitude()
    if mag is None and event.magnitudes:
        mag = event.magnitudes[0]
    return mag


def _arrival_lookup_for_pick(event, preferred_origin):
    """Return pick-id -> best P-arrival metadata, preferred origin first."""
    lookup = {}
    origins = [preferred_origin] + [
        o for o in event.origins if o is not preferred_origin
    ]
    for rank, org in enumerate(origins):
        for arr in getattr(org, "arrivals", []) or []:
            pid = str(arr.pick_id)
            phase = (arr.phase or "").strip().upper()
            if not phase.startswith("P") or pid in lookup:
                continue
            lookup[pid] = {
                "origin_rank": rank,
                "azimuth": as_float(arr.azimuth),
                "takeoff": as_float(arr.takeoff_angle),
                "distance_deg": as_float(arr.distance),
                "time_weight": as_float(arr.time_weight),
                "phase": phase,
            }
    return lookup


def _is_p_pick(pick, arrival_info=None):
    phase_hint = str(getattr(pick, "phase_hint", "") or "").strip().upper()
    if phase_hint:
        return phase_hint.startswith("P")
    if arrival_info is not None:
        return str(arrival_info.get("phase", "")).upper().startswith("P")
    return False


def extract_p_observations(
    event,
    origin,
    use_zero_weight=True,
    include_all_event_picks=True,
):
    """
    Extract P observations.

    Two deliberately separate modes are supported:

    COMPLETE mode (default)
        Start from all event-level P picks with waveform identifiers. This is
        the recommended mode for focal-mechanism work.

    V7-COMPATIBILITY mode (include_all_event_picks=False)
        Execute the original v7 preferred-origin-arrival loop literally.
        Therefore:
          * only arrivals belonging to the selected origin are considered;
          * with use_zero_weight=False, time_weight==0 arrivals are removed;
          * no additional NSLC deduplication or event-level pick recovery is
            performed.

    Keeping the two branches separate is important: compatibility mode should
    reproduce v7 exactly rather than approximately.
    """
    # ------------------------------------------------------------------
    # Exact v7 selection path.
    # ------------------------------------------------------------------
    if not include_all_event_picks:
        pick_map = {str(p.resource_id): p for p in event.picks}
        out = []

        for arr in origin.arrivals:
            phase = (arr.phase or "").strip().upper()
            if not phase.startswith("P"):
                continue

            weight = as_float(arr.time_weight)
            if (
                (not use_zero_weight)
                and np.isfinite(weight)
                and weight == 0.0
            ):
                continue

            p = pick_map.get(str(arr.pick_id))
            if p is None:
                continue

            wid = p.waveform_id
            net = (wid.network_code or "").strip()
            sta = (wid.station_code or "").strip()
            loc = normalize_loc(wid.location_code)
            cha = (wid.channel_code or "").strip()

            if not sta:
                continue

            out.append(
                PObservation(
                    pick_id=str(p.resource_id),
                    network=net,
                    station=sta,
                    location=loc,
                    channel=cha,
                    pick_time=p.time,
                    qml_azimuth=as_float(arr.azimuth),
                    qml_takeoff=as_float(arr.takeoff_angle),
                    qml_distance_deg=as_float(arr.distance),
                    qml_time_weight=weight,
                    manual_polarity=str(p.polarity or ""),
                )
            )

        if not out:
            raise ValueError(
                "No usable P arrivals were found in the selected origin."
            )
        return out

    # ------------------------------------------------------------------
    # Complete event-level selection path.
    # ------------------------------------------------------------------
    arrival_lookup = _arrival_lookup_for_pick(event, origin)
    candidates = []

    for p in event.picks:
        pid = str(p.resource_id)
        arr = arrival_lookup.get(pid)

        if not _is_p_pick(p, arr):
            continue

        if (
            not use_zero_weight
            and arr is not None
            and np.isfinite(arr["time_weight"])
            and arr["time_weight"] == 0.0
        ):
            continue

        wid = getattr(p, "waveform_id", None)
        if wid is None:
            continue

        net = (wid.network_code or "").strip()
        sta = (wid.station_code or "").strip()
        loc = normalize_loc(wid.location_code)
        cha = (wid.channel_code or "").strip()
        if not sta:
            continue

        if arr is None:
            az = takeoff = dist = weight = np.nan
            origin_rank = 999
        else:
            az = arr["azimuth"]
            takeoff = arr["takeoff"]
            dist = arr["distance_deg"]
            weight = arr["time_weight"]
            origin_rank = arr["origin_rank"]

        candidates.append(
            {
                "obs": PObservation(
                    pick_id=pid,
                    network=net,
                    station=sta,
                    location=loc,
                    channel=cha,
                    pick_time=p.time,
                    qml_azimuth=az,
                    qml_takeoff=takeoff,
                    qml_distance_deg=dist,
                    qml_time_weight=weight,
                    manual_polarity=str(p.polarity or ""),
                ),
                "origin_rank": origin_rank,
            }
        )

    if not candidates:
        raise ValueError(
            "No event-level P picks with waveform identifiers were found."
        )

    # Deduplicate exact NSLC only in COMPLETE mode.
    groups = {}
    for c in candidates:
        o = c["obs"]
        key = (o.network, o.station, o.location, o.channel)
        groups.setdefault(key, []).append(c)

    out = []
    for group in groups.values():
        group.sort(
            key=lambda c: (
                c["origin_rank"],
                c["obs"].pick_time,
            )
        )
        out.append(group[0]["obs"])

    out.sort(
        key=lambda o: (
            o.network,
            o.station,
            o.location,
            o.channel,
        )
    )
    return out


def load_station_metadata(path):
    df = pd.read_csv(path)

    required = {
        "Network Code",
        "Station Code",
        "Longitude (WGS84)",
        "Latitude (WGS84)",
        "Elevation",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Station CSV is missing required columns: {sorted(missing)}"
        )

    df = df.copy()
    df["Network Code"] = df["Network Code"].fillna("").astype(str).str.strip()
    df["Station Code"] = df["Station Code"].fillna("").astype(str).str.strip()
    df["Longitude (WGS84)"] = pd.to_numeric(
        df["Longitude (WGS84)"], errors="coerce"
    )
    df["Latitude (WGS84)"] = pd.to_numeric(
        df["Latitude (WGS84)"], errors="coerce"
    )
    df["Elevation"] = pd.to_numeric(df["Elevation"], errors="coerce")

    for c in ["Start Date", "End Date"]:
        if c in df.columns:
            df[c + "_parsed"] = pd.to_datetime(
            df[c], errors="coerce", utc=True, format="mixed"
        )

    return df


def station_row_for_pick(stations, net, sta, event_time):
    """
    Resolve station metadata robustly.

    Priority:
      1. exact network + station
      2. station-only match only when unique
      3. among duplicate epochs, choose epoch containing event time
      4. otherwise choose the row with valid coordinates nearest in start date
    """
    exact = stations[
        (stations["Network Code"] == net)
        & (stations["Station Code"] == sta)
    ].copy()

    if exact.empty:
        station_only = stations[stations["Station Code"] == sta].copy()
        nets = station_only["Network Code"].dropna().unique()
        if len(station_only) and len(nets) == 1:
            exact = station_only

    if exact.empty:
        return None, "station_not_in_metadata"

    exact = exact[
        exact["Longitude (WGS84)"].notna()
        & exact["Latitude (WGS84)"].notna()
    ].copy()
    if exact.empty:
        return None, "station_coordinates_missing"

    et = pd.Timestamp(event_time.datetime, tz="UTC")

    if "Start Date_parsed" in exact.columns:
        starts = exact["Start Date_parsed"]
        ends = exact.get(
            "End Date_parsed",
            pd.Series(pd.NaT, index=exact.index, dtype="datetime64[ns, UTC]"),
        )
        active = exact[
            (starts.isna() | (starts <= et))
            & (ends.isna() | (ends >= et))
        ]
        if len(active) == 1:
            return active.iloc[0], "exact_active_epoch"
        if len(active) > 1:
            active = active.sort_values("Start Date_parsed")
            return active.iloc[-1], "latest_active_epoch"

    if len(exact) == 1:
        return exact.iloc[0], "single_metadata_row"

    if "Start Date_parsed" in exact.columns:
        exact = exact.assign(
            _dt=(exact["Start Date_parsed"] - et).abs()
        ).sort_values("_dt")
    return exact.iloc[0], "duplicate_metadata_fallback"


def compute_geometry(origin, station_row):
    from obspy.geodetics import gps2dist_azimuth

    evlat = float(origin.latitude)
    evlon = float(origin.longitude)
    stalat = float(station_row["Latitude (WGS84)"])
    stalon = float(station_row["Longitude (WGS84)"])

    dist_m, az, baz = gps2dist_azimuth(evlat, evlon, stalat, stalon)
    return dist_m / 1000.0, az % 360.0, baz % 360.0


def _parse_pb1d_vp():
    """Return depth and Vp arrays from the embedded PB1D model."""
    rows = []
    for line in PB1Dvel.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        vals = [float(x) for x in line.split()]
        if len(vals) >= 2:
            rows.append((vals[0], vals[1]))
    arr = np.asarray(rows, dtype=float)
    return arr[:, 0], arr[:, 1]


PB=np.array([[float(v) for v in line.split()] for line in PB1Dvel.splitlines()])
BASIS=np.zeros((6,3,3))
for k,(i,j) in enumerate([(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]):
    BASIS[k,i,j]=1.; BASIS[k,j,i]=1.


def layered_ray(depth_km, distance_km, phase='P'):
    """Direct upgoing ray in horizontal PB1D layers; no head waves/reflections.

    Ray parameter is solved from horizontal offset using Snell's law.
    Density and speed at source are used for far-field radiation scaling.
    """
    from scipy.optimize import brentq
    depth=max(float(depth_km), 0.01)
    boundaries=np.unique(np.r_[0., PB[(PB[:,0]>0)&(PB[:,0]<depth),0], depth])
    dz=np.diff(boundaries)*1000.
    mid=(boundaries[:-1]+boundaries[1:])/2
    col=1 if phase=='P' else 2
    # PB entries are interface depths, use the layer value at its upper boundary.
    idx=np.searchsorted(PB[:,0],mid,side='right')-1
    v=PB[idx,col]*1000.
    density=PB[idx,3]*1000.
    x=float(distance_km)*1000.
    def horizontal(p):
        pv=np.clip(p*v,0,1-1e-13)
        return np.sum(dz*pv/np.sqrt(1-pv**2))
    if x<1e-8: pp=0.
    else: pp=brentq(lambda q: horizontal(q)-x,0.,(1-1e-12)/max(v),xtol=1e-17)
    pv=np.clip(pp*v,0,1-1e-13)
    travel=float(np.sum(dz/(v*np.sqrt(1-pv**2))))
    # Direction from source towards receiver, in NED coordinates.
    source_sin=float(pp*v[-1]); source_cos=np.sqrt(max(0.,1-source_sin**2))
    return travel,source_sin,source_cos,float(v[-1]),float(density[-1])


def gaussian_rate_at(times, center, duration):
    sigma=max(float(duration)/2.355, 0.03)
    return np.exp(-0.5*((times-center)/sigma)**2)/(sigma*np.sqrt(2*np.pi))


def generate_layered_design(azimuth_deg, distance_km, depth_km, dt, npts,
                            start_relative, duration, measured_p=None,
                            source_delay=0., phase='P', output='VEL'):
    """Layered direct-ray far-field P/S moment-rate displacement kernel (m/Nm).

    Uses PB1D Snell rays and source-local material properties. No claim to
    include free-surface, reflections, conversions, attenuation, or exact
    geometrical spreading. Suitable for diagnostic P-onset inversion only.
    """
    az=np.deg2rad(azimuth_deg)
    radius=max(100.,np.hypot(distance_km*1000.,depth_km*1000.))
    times=start_relative+np.arange(npts)*dt
    design=np.zeros((npts,3,6),float)
    phases=('P',) if phase=='P' else ('P','S')
    for ph in phases:
        tt,ss,cc,v,rho=layered_ray(depth_km,distance_km,ph)
        n=np.array([ss*np.cos(az),ss*np.sin(az),-cc])
        # The P arrival may be aligned to the catalog pick, but the ray
        # direction and velocity still come from the layered PB1D model.
        arrival=(measured_p if (ph=='P' and measured_p is not None) else tt)+source_delay
        # Picks mark onset, not the center of a symmetric source pulse.
        # The Gaussian center follows onset by approximately half the duration.
        arrival += 0.5*duration
        pulse=gaussian_rate_at(times,arrival,duration)
        if output == 'VEL':
            sigma=max(float(duration)/2.355,0.03)
            pulse=-(times-arrival)/sigma**2*pulse
        factor=1./(4*np.pi*rho*v**3*radius)
        for j,B in enumerate(BASIS):
            mn=B@n
            if ph=='P': radiation=n*(n@mn)
            else: radiation=mn-n*(n@mn)
            design[:,:,j]+=factor*pulse[:,None]*radiation[None,:]
    return design


def helmholtz_tensor(freq, xyz, vp, vs, rho):
    """Homogeneous full-space frequency-domain displacement Green tensor.

    numpy irfft convention requires exp(-i omega r/v) for a causal delay.
    Retained for independent kernel checks; main inversion uses direct rays.
    """
    f=np.asarray(freq,float);x=np.asarray(xyz,float)
    r=np.linalg.norm(x);n=x/r;omega=2*np.pi*f
    mu=rho*vs**2;ks=omega/vs;kp=omega/vp
    good=f>0
    ss=np.zeros(len(f),complex);pp=ss.copy()
    ss[good]=np.exp(-1j*ks[good]*r)/(4*np.pi*r)
    pp[good]=np.exp(-1j*kp[good]*r)/(4*np.pi*r)
    ds=(-1j*ks-1/r)*ss;dp=(-1j*kp-1/r)*pp
    dds=(-ks**2+2j*ks/r+2/r**2)*ss
    ddp=(-kp**2+2j*kp/r+2/r**2)*pp
    A=ss/mu;D=np.zeros_like(ss);Q=np.zeros_like(ss)
    D[good]=((ds[good]-dp[good])/r)/(mu*ks[good]**2)
    Q[good]=((dds[good]-ddp[good])-(ds[good]-dp[good])/r)/(mu*ks[good]**2)
    return (A+D)[:,None,None]*np.eye(3)[None,:,:]+Q[:,None,None]*(n[:,None]*n[None,:])[None,:,:]


def moment_transfer(freq,xyz,vp,vs,rho,step_m=2.):
    r=np.linalg.norm(xyz);h=min(step_m,max(.02,r*1e-5))
    grad=np.empty((len(freq),3,3,3),complex)
    for k in range(3):
        shift=np.zeros(3);shift[k]=h
        grad[:,:,:,k]=(helmholtz_tensor(freq,xyz+shift,vp,vs,rho)-
                         helmholtz_tensor(freq,xyz-shift,vp,vs,rho))/(2*h)
    return -np.einsum('fijk,mjk->fim',grad,BASIS,optimize=True)


def bandpass(x,dt,lo,hi):
    nyq=.5/dt
    if not (0<lo<hi<nyq):raise ValueError('Invalid bandpass / sampling')
    sos=butter(4,[lo/nyq,hi/nyq],btype='band',output='sos')
    return sosfiltfilt(sos,x,axis=0)


def gaussian_moment_rate(t,center,duration):
    sigma=duration/2.355
    rate=np.exp(-.5*((t-center)/sigma)**2)
    return rate/(np.sum(rate)*(t[1]-t[0]))


# The old FFT moment-history generator has been replaced by the explicit
# causal layered-ray moment-rate design above.


def ned_to_rtp(M):
    # RTP: r=Up, theta=South, phi=East
    T=np.array([[0,0,-1],[-1,0,0],[0,1,0.]])
    R=T@M@T.T
    return [R[0,0],R[1,1],R[2,2],R[0,1],R[0,2],R[1,2]]


def matrix_from_coeff(c):return np.einsum('m,mij->ij',c,BASIS)


def fit_design(stations, damping=.03, iso='full', robust_iters=4):
    """Joint robust WLS, station-equalized and noise-weighted; six or five DOF.
    A and y are scaled by physical reference moment, and a global tensor is
    recovered. Station gains are NOT independently optimized.
    """
    ref=1e15
    if iso=='deviatoric':
        C=np.array([[1,0],[0,1],[-1,-1],[0,0],[0,0],[0,0]],float)
        C=np.concatenate([C,np.eye(6)[:,3:]],axis=1)
    else:C=np.eye(6)
    chunks=[]; targets=[]; meta=[]
    for s in stations:
        A=(s['design']*ref).reshape(-1,6)@C
        y=s['observed'].reshape(-1)
        # Normalize station weight by noise and number of samples; cap very
        # low noise to avoid domination by a single station.
        sigma=max(s['noise'],1e-12)
        # Station balancing: prevent high-SNR sites from overwhelming the solution.
        # The observed P-window RMS also limits the weight of very quiet stations.
        signal_rms=float(np.sqrt(np.mean(y*y)))
        w=1/(max(sigma, 0.25*signal_rms, 1e-12)*np.sqrt(len(y)))
        chunks.append(A*w);targets.append(y*w)
        meta.append((s['id'],sigma))
    A=np.vstack(chunks);y=np.concatenate(targets)
    scale=np.maximum(np.linalg.norm(A,axis=0),1e-30)
    An=A/scale
    w=np.ones(len(y))
    for _ in range(robust_iters):
        Aw=An*w[:,None];yw=y*w
        aug=np.vstack([Aw,damping*np.eye(An.shape[1])]);target=np.r_[yw,np.zeros(An.shape[1])]
        v=lstsq(aug,target,lapack_driver='gelsy')[0]
        res=y-An@v
        med=np.median(np.abs(res-np.median(res)))+1e-12
        w=np.sqrt(np.clip(1.345*1.4826*med/np.maximum(np.abs(res),1e-30),.1,1.))
    coeff=ref*(C@(v/scale))
    return coeff,float(np.linalg.cond(An)),meta



def download_inventory_for_waveforms(stream, picks, start, end, output_dir,
                                     providers, local_inventory=None):
    """Response metadata ONLY; never download waveforms or change NSLC identities.

    Search by actual waveform NSLC and acquisition time, not just the P-pick
    network/station. Persist each successful StationXML response for offline reuse.
    No provider is guaranteed to archive every temporary network (e.g. 4O).
    """
    from obspy import read_inventory
    from obspy.core.inventory import Inventory
    import re
    cache = output_dir / 'stationxml_cache'
    cache.mkdir(parents=True, exist_ok=True)
    inv = Inventory(networks=[], source='TexNet MT station response cache')
    if local_inventory:
        inv += read_inventory(str(local_inventory))
    clients = {}
    report = []
    ids = sorted({(tr.stats.network, tr.stats.station, tr.stats.location,
                   tr.stats.channel) for tr in stream if tr.stats.channel})
    # Limit requests to stations actually identified by original QuakeML picks.
    picked = {(o.network, o.station) for o in picks}
    ids = [x for x in ids if x[:2] in picked]
    for net, sta, loc, cha in ids:
        seed = '.'.join((net, sta, loc, cha))
        try:
            inv.get_response(seed, start + (end-start)/2)
            report.append(dict(seed=seed, status='supplied_inventory'))
            continue
        except Exception:
            pass
        tag = re.sub(r'[^A-Za-z0-9_.-]', '_', f'{net}.{sta}.{loc or "--"}.{cha}')
        target = cache / (tag + '.xml')
        if target.exists():
            try:
                cached = read_inventory(str(target))
                cached.get_response(seed, start + (end-start)/2)
                inv += cached
                report.append(dict(seed=seed, status='cache', provider=str(target)))
                continue
            except Exception:
                target.rename(target.with_suffix('.invalid.xml'))
        errors = []
        for provider in providers:
            try:
                if provider not in clients:
                    clients[provider] = Client(provider, timeout=18)
                got = clients[provider].get_stations(
                    network=net, station=sta, location=loc or '--', channel=cha,
                    starttime=start, endtime=end, level='response')
                got.get_response(seed, start + (end-start)/2)
                got.write(str(target), format='STATIONXML')
                inv += got
                report.append(dict(seed=seed, status='downloaded', provider=provider))
                print('RESPONSE OK', seed, provider)
                break
            except Exception as exc:
                errors.append(f'{provider}: {type(exc).__name__}: {str(exc)[:95]}')
        else:
            report.append(dict(seed=seed, status='unavailable', errors=' | '.join(errors)))
            print('RESPONSE UNAVAILABLE', seed, '; '.join(errors)[:240])
    pd.DataFrame(report).to_csv(output_dir / 'inventory_qc.csv', index=False)
    if inv.networks:
        inv.write(str(output_dir / 'available_station_responses.xml'), format='STATIONXML')
    return inv


def preprocess_station_3c(stream, obs, origin, inv, start, end, dt, lo, hi,
                          min_window=18., min_pre_pick=2., response_margin=8., output="VEL"):
    """Adaptive real-data window, never pad absent samples.

    Match the original QuakeML network/station/channel family. Require three
    oriented response-calibrated channels, find their common overlap, and
    select a pick-centered segment. Extended data are used for response
    deconvolution before final trimming. Return (data, reason).
    """
    groups = {}
    for tr in stream:
        if tr.stats.network != obs.network or tr.stats.station != obs.station:
            continue
        if obs.location and tr.stats.location != obs.location:
            continue
        if obs.channel and tr.stats.channel[:2] != obs.channel[:2]:
            continue
        key = (tr.stats.network, tr.stats.station, tr.stats.location,
               tr.stats.channel[:2])
        groups.setdefault(key, []).append(tr)
    if not groups:
        return None, 'no_matching_mseed_channels'
    reasons = []
    for key, trs in groups.items():
        ident = '.'.join(key)
        try:
            st = Stream([tr.copy() for tr in trs])
            st.sort(keys=['network', 'station', 'location', 'channel', 'starttime'])
            st.merge(method=0, fill_value=None)
            if len(st) != 3 or len({tr.stats.channel for tr in st}) != 3:
                raise ValueError(f'expected_3_unique_channels_got_{len(st)}')
            # A single continuous segment is required for each channel. Do
            # not interpolate across miniSEED gaps or manufacture samples.
            for tr in st:
                if np.ma.isMaskedArray(tr.data) and np.ma.getmaskarray(tr.data).any():
                    raise ValueError('unresolved_mseed_gaps')
                if not np.isfinite(tr.data).all():
                    raise ValueError('nonfinite_samples')
            overlap_start = max(tr.stats.starttime for tr in st)
            overlap_end = min(tr.stats.endtime for tr in st)
            pick = obs.pick_time
            # Requested origin window is an upper bound, not a mandatory
            # coverage requirement. The P pick must lie within usable data.
            target_start = max(overlap_start, start, pick - max(min_pre_pick, 30.))
            target_end = min(overlap_end, end)
            if target_start > pick - min_pre_pick:
                raise ValueError(f'not_enough_pre_P_data:overlap={overlap_start}/{overlap_end}:P={pick}')
            if target_end - target_start < min_window:
                raise ValueError(f'insufficient_common_window:{target_end-target_start:.1f}s'
                                 f':overlap={overlap_start}/{overlap_end}')
            # Keep as much available margin as possible around final window.
            processing_start = max(overlap_start, target_start - response_margin)
            processing_end = min(overlap_end, target_end + response_margin)
            if processing_end - processing_start < min_window:
                raise ValueError('insufficient_processing_window')
            st.trim(processing_start, processing_end, pad=False)
            for tr in st:
                try:
                    response=inv.get_response(tr.id, pick)
                    inv.get_orientation(tr.id, pick)
                    if response.instrument_sensitivity is None:
                        raise ValueError('missing_instrument_sensitivity')
                    inunit=str(response.instrument_sensitivity.input_units).upper().replace(' ','')
                    if inunit not in ('M','M/S','M/S**2','M/S^2'):
                        raise ValueError(f'unsupported_response_input_units:{inunit}')
                except Exception as exc:
                    raise ValueError(f'missing_response_or_orientation:{tr.id}:{exc}')
                nyq = tr.stats.sampling_rate / 2
                if nyq <= hi * 2:
                    raise ValueError('insufficient_native_sampling_rate')
                pf = (max(.001, lo*.25), lo*.6, hi*1.5,
                      min(nyq*.9, hi*2.5))
                if not (0 < pf[0] < pf[1] < pf[2] < pf[3] < nyq):
                    raise ValueError('invalid_response_prefilter')
                tr.detrend('demean')
                tr.detrend('linear')
                tr.taper(max_percentage=.05)
                tr.remove_response(inventory=inv, output=output,
                                   pre_filt=pf, water_level=60)
            # Resample after response removal and use the same exact timestamps
            # for every channel; small sampling-phase differences are allowed.
            npts = int(np.floor((target_end-target_start)/dt)) + 1
            if npts < 32:
                raise ValueError('too_few_samples')
            for tr in st:
                tr.interpolate(sampling_rate=1/dt, method='lanczos', a=12,
                               starttime=target_start, npts=npts)
            ori = [inv.get_orientation(tr.id, pick) for tr in st]
            z, n, e = rotate2zne(
                st[0].data, ori[0]['azimuth'], ori[0]['dip'],
                st[1].data, ori[1]['azimuth'], ori[1]['dip'],
                st[2].data, ori[2]['azimuth'], ori[2]['dip'])
            data = bandpass(np.column_stack([n,e,-z]), dt, lo, hi)
            if not np.isfinite(data).all():
                raise ValueError('nonfinite_processed_displacement')
            return dict(id=ident, data=data, channels=[tr.id for tr in st],
                        start=target_start, end=target_start+(npts-1)*dt,
                        overlap_start=overlap_start, overlap_end=overlap_end,
                        pick=pick), 'accepted'
        except Exception as exc:
            reasons.append(f'{ident}:{type(exc).__name__}:{exc}')
    return None, ' | '.join(reasons)[:1200]

def build_pyfk_kernels(stations, args, origin):
    """Compute layered FK Green functions once for all receiver distances.

    Six unit NED tensors (1e15 N m) produce SI NED displacement/velocity.
    The GF's SAC b is the physical origin-relative first sample time.
    """
    try:
        from pyfk import Config, SeisModel, SourceModel, calculate_gf, calculate_sync
        from obspy import Trace
    except ImportError as exc:
        raise RuntimeError('Install pyfk (pip install pyfk) before running') from exc
    layers = PB[PB[:, 0] >= 0].copy()
    depths = layers[:, 0]
    thick = np.r_[np.diff(depths), 0.0]
    # PyFK: thickness, Vs, Vp, density, Qs, Qp.
    model_data = np.column_stack([thick, layers[:, 2], layers[:, 1],
                                  layers[:, 3], layers[:, 5], layers[:, 4]])
    model = SeisModel(model=model_data)
    source = SourceModel(sdep=max(.01, float(origin.depth)/1000), srcType='dc')
    distances = np.array([max(.01, st['distance_km']) for st in stations])
    # Keep all station distances in one FK call for consistent wavenumber integration.
    npt = int(2**np.ceil(np.log2(max(512, (args.pre+args.post+80)/args.dt))))
    config = Config(model=model, source=source, receiver_distance=distances,
                    npt=npt, dt=args.dt, rdep=0., updn='all',
                    samples_before_first_arrival=int(round(12/args.dt)),
                    dk=args.fk_dk, kmax=args.fk_kmax)
    print(f'Computing PyFK layered GFs for {len(distances)} distances, npt={npt} ...', flush=True)
    gfs = calculate_gf(config)
    # STF must be causal and its discrete samples sum to one (pyfk convention).
    t = np.arange(max(3, int(np.ceil(args.duration*5/args.dt)))) * args.dt
    sigma = max(args.duration/2.355, args.dt)
    rate = np.exp(-.5*((t-2*sigma)/sigma)**2)
    rate /= rate.sum()
    stf = Trace(data=rate.astype(np.float64)); stf.stats.delta = args.dt
    ref_moment = 1e15
    # PyFK 7-vector takes moment in dyne-cm, NOT in units of 1e20.
    # Its calculate_radiation_pattern internally multiplies m0 by 1e-20.
    # 1 N m = 1e7 dyne-cm; 1e15 N m = 1e22 dyne-cm.
    m0_pyfk = ref_moment * 1e7
    for j, B in enumerate(BASIS):
        source.update_source_mechanism(np.r_[m0_pyfk,
            B[0,0], B[0,1], B[0,2], B[1,1], B[1,2], B[2,2]])
        for i, st in enumerate(stations):
            syn = calculate_sync(gfs[i], config, float(st['azimuth']), stf)[0]
            z, r, transverse = (np.asarray(tr.data, float) * .01 for tr in syn)
            az = np.deg2rad(st['azimuth'])
            # Z is positive UP; R points source -> station; T is clockwise.
            ned = np.column_stack([r*np.cos(az)-transverse*np.sin(az),
                                   r*np.sin(az)+transverse*np.cos(az), -z])
            if args.physical_output == 'VEL':
                ned = np.gradient(ned, args.dt, axis=0)
            b = float(gfs[i][0].stats.sac.b)
            # The same zero-phase filter is applied to observed and synthetic.
            ned = bandpass(ned, args.dt, args.low, args.high)
            if j == 0:
                st['fk_basis'] = np.zeros((len(ned), 3, 6))
                st['fk_start_s'] = b
            st['fk_basis'][:,:,j] = ned / ref_moment
    for st in stations:
        if not np.isfinite(st['fk_basis']).all():
            raise RuntimeError(f'Nonfinite PyFK Green function: {st["id"]}')
        if np.max(np.abs(st['fk_basis'] * ref_moment)) < 1e-20:
            raise RuntimeError(f'Near-zero PyFK Green function: {st["id"]}; max SI amplitude for 1e15 Nm={np.max(np.abs(st["fk_basis"] * ref_moment)):.3e}')


def sample_pyfk_kernel(st, shift, args):
    """Interpolate physical-time FK kernels to the observed station sample times."""
    target = st['start_relative_s'] + (st['fit_first'] +
              np.arange(len(st['observed']))) * args.dt
    # Align theoretical P arrival with observed pick if requested; do not
    # re-center source pulse at P pick. A global shift remains optional.
    correction = st['p_timing_correction_s'] if args.align_picks and not args.no_pick_alignment else 0.
    source_times = st['fk_start_s'] + np.arange(len(st['fk_basis'])) * args.dt
    query = target - correction - args.source_delay - shift
    result = np.zeros((len(target), 3, 6))
    for c in range(3):
        for j in range(6):
            result[:,c,j] = np.interp(query, source_times,
                                     st['fk_basis'][:,c,j], left=0., right=0.)
    return result


def main():
    p=argparse.ArgumentParser(description='TexNet local-file full MT baseline; original event/pick/station conventions')
    p.add_argument('--qml',type=Path,default=DEFAULT_QML)
    p.add_argument('--mseed',type=Path,default=DEFAULT_MSEED)
    p.add_argument('--stations',type=Path,default=DEFAULT_STATIONS)
    p.add_argument('--output-dir',type=Path,default=Path(f'{eid}_moment_tensor'))
    p.add_argument('--inventory',type=Path,help='StationXML response/orientation metadata; recommended for reproducibility')
    p.add_argument('--fdsn',default='EARTHSCOPE',help='First station-metadata provider; no waveform downloads')
    p.add_argument('--metadata-providers',default='http://rtserve.beg.utexas.edu,EARTHSCOPE,RESIF,GFZ',help='Comma-separated fallback FDSN station services')
    p.add_argument('--dt',type=float,default=.5)
    p.add_argument('--low',type=float,default=1/30)
    p.add_argument('--high',type=float,default=1/15)
    p.add_argument('--pre',type=float,default=30.)
    p.add_argument('--min-window',type=float,default=18.,help='Minimum usable 3C seconds')
    p.add_argument('--min-pre-pick',type=float,default=2.,help='Minimum seconds before P pick')
    p.add_argument('--response-margin',type=float,default=8.,help='Extra available seconds for deconvolution')
    p.add_argument('--post',type=float,default=120.)
    p.add_argument('--duration',type=float,default=1.0)
    p.add_argument('--source-delay',type=float,default=0.)
    p.add_argument('--min-snr',type=float,default=1.5)
    p.add_argument('--snr-noise-seconds',type=float,default=20.,help='Maximum pre-P noise interval in seconds')
    p.add_argument('--snr-signal-seconds',type=float,default=40.,help='Post-P signal interval in seconds')
    p.add_argument('--min-noise-seconds',type=float,default=10.,help='Minimum pre-P interval for trustworthy long-period SNR')
    p.add_argument('--min-stations',type=int,default=5)
    p.add_argument('--fit-phase',choices=['P','all'],default='all',help='Fit P onset window (recommended for approximate full-space kernel) or all phases')
    p.add_argument('--p-window',type=float,default=4.,help='Seconds after P pick included in inversion')
    p.add_argument('--align-picks',action=argparse.BooleanOptionalAction,default=True,help='Align modeled P onset with QuakeML P pick')
    p.add_argument('--max-distance',type=float,default=250.)
    p.add_argument('--damping',type=float,default=.03)
    p.add_argument('--tensor-type',choices=['full','deviatoric'],default='deviatoric')
    p.add_argument('--fit-components',choices=['3C','P'],default='3C',help='P projects onto modeled direct-P polarization; 3C retains all components')
    p.add_argument('--fit-pre-p',type=float,default=1.0,help='Seconds before P arrival retained in inversion')
    p.add_argument('--exclude-zero-weight-arrivals',action='store_true')
    p.add_argument('--show',action='store_true')
    p.add_argument('--physical-output', choices=['VEL','DISP'],default='DISP',help='VEL avoids low-frequency displacement drift')
    p.add_argument('--max-pick-shift',type=float,default=3.0,help='Grid search global source pulse center offset (seconds)')
    p.add_argument('--station-shift-max',type=float,default=4.,help='Maximum station-specific 3C time correction (s); 0 disables')
    p.add_argument('--station-shift-step',type=float,default=.5,help='Station shift grid spacing (s)')
    p.add_argument('--station-shift-iterations',type=int,default=2,help='Alternating bounded station timing and tensor fits')
    p.add_argument('--fk-dk',type=float,default=.2)
    p.add_argument('--fk-kmax',type=float,default=20.)
    p.add_argument('--max-station-peak',type=float,default=0.0,help='Reject extremely large calibrated traces in output SI units; 0 disables')
    p.add_argument('--no-pick-alignment',action='store_true',help='Use PB1D predicted direct-P time instead of QuakeML P pick')
    p.add_argument('--texnet-band',choices=['15-30','10-20','custom'],default='15-30',
                   help='TexNet operations manual long-period bands; custom uses --low/--high')
    args=p.parse_args()
    if args.texnet_band == '15-30':
        args.low,args.high=1/30,1/15
    elif args.texnet_band == '10-20':
        args.low,args.high=1/20,1/10
    print(f'TexNet-style band: {args.low:.5f}-{args.high:.5f} Hz; output={args.physical_output}; dt={args.dt}s')
    for path in [args.qml,args.mseed,args.stations]:
        if not path.exists():raise FileNotFoundError(path)
    if not (0<args.low<args.high<.5/args.dt):raise ValueError('Invalid band')
    if args.physical_output != 'DISP':
        warnings.warn('TexNet published operational MT inversion is long-period waveform based; DISP is recommended for the baseline')
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    event=read_events(str(args.qml))[0];origin=get_preferred_origin(event)
    stream=read(str(args.mseed)); station_df=load_station_metadata(args.stations)
    # Identical original QuakeML P-pick and station-CSV matching conventions.
    picks=extract_p_observations(event,origin,use_zero_weight=not args.exclude_zero_weight_arrivals,
                                 include_all_event_picks=not args.exclude_zero_weight_arrivals)
    start=origin.time-args.pre;end=origin.time+args.post
    providers = list(dict.fromkeys(['http://rtserve.beg.utexas.edu', args.fdsn] + [x.strip() for x in
        args.metadata_providers.split(',') if x.strip()]))
    inv = download_inventory_for_waveforms(stream, picks, start, end, out,
                                           providers, args.inventory)
    used=set();accepted=[];qc=[]
    for obs in picks:
        key=(obs.network,obs.station)
        if key in used:continue
        used.add(key)
        row,why=station_row_for_pick(station_df,obs.network,obs.station,origin.time)
        if row is None:
            qc.append(dict(network=obs.network,station=obs.station,status=why));continue
        distance,az,baz=compute_geometry(origin,row)
        if distance>args.max_distance:
            qc.append(dict(network=obs.network,station=obs.station,status='outside_distance'));continue
        data,reason=preprocess_station_3c(stream,obs,origin,inv,start,end,args.dt,args.low,args.high,
                                          args.min_window,args.min_pre_pick,args.response_margin,args.physical_output)
        if data is None:
            qc.append(dict(network=obs.network,station=obs.station,status='rejected_3C',reason=reason));continue
        y=data['data']
        if args.max_station_peak>0 and np.max(np.abs(y))>args.max_station_peak:
            qc.append(dict(network=obs.network,station=obs.station,status='amplitude_qc_rejected',reason=f'peak={np.max(np.abs(y)):.5g} {args.physical_output}'))
            continue
        preidx=int(np.floor((obs.pick_time-data['start'])/args.dt))
        if preidx < max(5,int(args.min_pre_pick/args.dt)):
            qc.append(dict(network=obs.network,station=obs.station,status='insufficient_pre_P_noise',
                           available_pre_P_s=float(obs.pick_time-data['start'])));continue
        # Long-period QC: compare comparable finite intervals, not 3 s of noise
        # with up to 120 s of signal. Do not pretend short pre-P records
        # establish long-period noise statistics.
        n_noise=min(preidx,int(round(args.snr_noise_seconds/args.dt)))
        n_signal=min(len(y)-preidx,int(round(args.snr_signal_seconds/args.dt)))
        if n_noise < int(round(args.min_noise_seconds/args.dt)):
            qc.append(dict(network=obs.network,station=obs.station,
                           status='insufficient_long_period_noise',
                           available_pre_P_s=n_noise*args.dt));continue
        if n_signal < int(round(10./args.dt)):
            qc.append(dict(network=obs.network,station=obs.station,
                           status='insufficient_post_P_signal',
                           available_post_P_s=n_signal*args.dt));continue
        noise_samples=y[preidx-n_noise:preidx]
        signal=y[preidx:preidx+n_signal]
        noise=float(np.sqrt(np.mean(noise_samples**2)))
        signal_rms=float(np.sqrt(np.mean(signal**2)))
        snr=signal_rms/max(noise,1e-20)
        if not np.isfinite(snr) or snr<args.min_snr or noise<=0:
            qc.append(dict(network=obs.network,station=obs.station,
                           status='low_snr',snr=snr,noise_rms=noise,
                           signal_rms=signal_rms,noise_seconds=n_noise*args.dt,
                           signal_seconds=n_signal*args.dt));continue
        azr=np.deg2rad(az);xyz=np.array([distance*1000*np.cos(azr),distance*1000*np.sin(azr),-origin.depth])
        measured_p=float(obs.pick_time-origin.time)
        p_ray=layered_ray(origin.depth/1000,distance,'P')
        timing_correction=measured_p-p_ray[0]
        G=np.zeros((len(y),3,6),dtype=float)  # PyFK basis computed in batch after station QC
        # Optionally fit only a short P window; full 3C fitting is supported by PyFK.
        if args.fit_phase=='P':
            last=min(len(y),preidx+int(round(args.p_window/args.dt)))
            if last-preidx<12:
                qc.append(dict(network=obs.network,station=obs.station,status='too_short_P_window'))
                continue
            first=max(0,preidx-int(round(args.fit_pre_p/args.dt)))
            y_fit=y[first:last].copy()
            G_fit=G[first:last].copy()
        else:
            y_fit=y
            G_fit=G
        if args.fit_components=='P':
            # The direct-P approximation cannot explain transverse/S-wave motion.
            # Project both observations and kernels onto the same P polarization.
            _,ss,cc,_,_=p_ray
            ar=np.deg2rad(az)
            pol=np.array([ss*np.cos(ar),ss*np.sin(ar),-cc])
            y_fit=(y_fit@pol)[:,None]
            G_fit=np.einsum('tcm,c->tm',G_fit,pol)[:,None,:]
        accepted.append(dict(id=data['id'],observed=y_fit,design=G_fit,noise=noise,snr=snr,
                              azimuth=az,distance_km=distance,
                              p_timing_correction_s=timing_correction,
                              geometry=(az,distance,origin.depth/1000),measured_p=measured_p,
                              start_relative_s=float(data['start']-origin.time),
                              fit_first=first if args.fit_phase=='P' else 0,
                              p_polarization=pol if args.fit_components=='P' else None,
                              full_npts=len(y)))
        qc.append(dict(network=obs.network,station=obs.station,status='accepted',snr=snr,noise_seconds=n_noise*args.dt,signal_seconds=n_signal*args.dt,distance_km=distance,azimuth=az,
                       window_start=str(data['start']),window_end=str(data['end']),
                       overlap_start=str(data['overlap_start']),overlap_end=str(data['overlap_end'])))
    pd.DataFrame(qc).to_csv(out/'station_qc.csv',index=False)
    if len(accepted)<args.min_stations:
        from collections import Counter
        reasons=Counter(str(r.get('reason',r.get('status','unknown'))).split(':')[0] for r in qc)
        raise RuntimeError(f'Only {len(accepted)} stations passed QC (need {args.min_stations}). '
            f'Rejection groups: {dict(reasons)}. Inspect {out}/station_qc.csv and '
            f'{out}/inventory_qc.csv. If all responses are unavailable, obtain the '
            'deployment-specific 4O StationXML from its operator; counts cannot be '
            'converted to physical displacement without valid response metadata.')
    build_pyfk_kernels(accepted, args, origin)
    def build_fit_kernel(st, shift):
        g = sample_pyfk_kernel(st, shift, args)
        if st['p_polarization'] is not None:
            g = np.einsum('tcm,c->tm', g, st['p_polarization'])[:,None,:]
        return g

    best=None
    offsets=np.linspace(-args.max_pick_shift,args.max_pick_shift,13)
    for shift in offsets:
        for st in accepted:
            st['design']=build_fit_kernel(st,shift)
        c,condition,_=fit_design(accepted,args.damping,args.tensor_type,robust_iters=1)
        numer=sum(np.sum((st['observed']-np.einsum('tcm,m->tc',st['design'],c))**2) for st in accepted)
        denom=sum(np.sum(st['observed']**2) for st in accepted)
        score=1-numer/max(denom,1e-30)
        if best is None or score>best[0]:best=(score,shift,c,condition)
    _,best_shift,_,_=best
    if np.isclose(abs(best_shift), args.max_pick_shift):
        warnings.warn('Best shift is at search boundary: source-time/phase timing remains unresolved')
    # Estimate bounded, shared 3C station timing corrections with the same
    # forward model. Refit the tensor after each timing pass; never independently
    # shift N, E and D (which would corrupt polarization).
    for st in accepted:
        st['station_shift_s'] = 0.0
        st['design'] = build_fit_kernel(st, best_shift)
    coeff,cond,_=fit_design(accepted,args.damping,args.tensor_type,robust_iters=4)
    if args.station_shift_max > 0 and args.station_shift_iterations > 0:
        shifts=np.arange(-args.station_shift_max, args.station_shift_max +
                         .25*args.station_shift_step, args.station_shift_step)
        for iteration in range(args.station_shift_iterations):
            for st in accepted:
                obs=st['observed']
                # Use fixed current tensor and observed energy for each shift;
                # require an actual residual reduction relative to zero correction.
                candidates=[]
                for ds in shifts:
                    design=build_fit_kernel(st,best_shift+float(ds))
                    syn=np.einsum('tcm,m->tc',design,coeff)
                    misfit=float(np.sum((obs-syn)**2))
                    candidates.append((misfit,abs(float(ds)),float(ds),design))
                best_local=min(candidates,key=lambda v:(v[0],v[1]))
                st['station_shift_s']=best_local[2]
                st['design']=best_local[3]
            coeff,cond,_=fit_design(accepted,args.damping,args.tensor_type,robust_iters=4)
            print(f'Station timing iteration {iteration+1}: shifts (s): '+
                  ', '.join(f"{st['id']}={st['station_shift_s']:+.1f}" for st in accepted),flush=True)
    # Record the actual station-specific shifts and keep the station count fixed.
    numer=sum(np.sum((st['observed']-np.einsum('tcm,m->tc',st['design'],coeff))**2) for st in accepted)
    denom=sum(np.sum(st['observed']**2) for st in accepted)
    final_vr=100*(1-numer/max(denom,1e-30))
    print('Best global pulse shift (s):',best_shift,'global VR:',final_vr)
    print('Operator condition number:',cond)
    if cond>1e8:warnings.warn('Ill-conditioned moment-tensor operator')
    M=matrix_from_coeff(coeff); M0=np.linalg.norm(M)/np.sqrt(2)
    results=[]
    for s in accepted:
        fit=np.einsum('tcm,m->tc',s['design'],coeff);s['fit']=fit
        vr=100*(1-np.sum((s['observed']-fit)**2)/max(np.sum(s['observed']**2),1e-30))
        results.append(dict(station=s['id'],vr_percent=vr,snr=s['snr'],distance_km=s['distance_km'],azimuth=s['azimuth'],observed_peak_m=float(np.max(np.abs(s['observed']))),synthetic_peak_m=float(np.max(np.abs(fit))),amplitude_ratio=float(np.max(np.abs(fit))/max(np.max(np.abs(s['observed'])),1e-30)),station_shift_s=s['station_shift_s']))
    pd.DataFrame(results).to_csv(out/'station_fits.csv',index=False)
    summary=dict(source_pulse_center_relative_to_pick_s=None,
                 fit_components=args.fit_components, source_duration_s=args.duration, frequency_band_hz=[args.low,args.high], sampling_interval_s=args.dt, texnet_band=args.texnet_band, method='PyFK layered full-waveform Green functions (ZRT to NED), PB1D model',tensor_NED_Nm=M.tolist(),
                 tensor_RTP_Nm=ned_to_rtp(M),scalar_moment_proxy_Nm=M0,condition=cond,best_pulse_shift_s=float(best_shift),
                 physical_output=args.physical_output,global_VR_percent=float(final_vr),
                 station_count=len(accepted),station_shifts_s={st['id']:st['station_shift_s'] for st in accepted},mean_VR_percent=float(np.mean([r['vr_percent'] for r in results])),
                 waveform_source=str(args.mseed),event_source=str(args.qml),station_source=str(args.stations),
                 warning='Station timing shifts are fitted nuisance parameters, not validated travel-time corrections. Layered 1D PyFK inversion; source depth, velocity model, station response, STF and timing must be validated; not publication-validated')
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    fig=plt.figure(figsize=(15,max(9,1.5*min(12,len(accepted)))))
    from matplotlib.gridspec import GridSpec
    n=min(12,len(accepted));gs=GridSpec(n,4,figure=fig,width_ratios=[1,1,1,1],hspace=.5,wspace=.3)
    # Each station has its own real-data window; time axes cannot be shared.
    for i,s in enumerate(accepted[:n]):
        for j,c in enumerate('P' if args.fit_components=='P' else 'NED'):
            ax=fig.add_subplot(gs[i,j]);a=s['observed'][:,j];b=s['fit'][:,j]
            scale=max(np.max(np.abs(a)),np.max(np.abs(b)),1e-20)
            t=np.arange(len(a))*args.dt+s['start_relative_s']+s['fit_first']*args.dt
            ax.plot(t,a/scale,color='#222222',lw=1.,label='Observed');ax.plot(t,b/scale,color='#d44b46',lw=1.,label='Synthetic')
            ax.set_ylim(-1.15,1.15);ax.grid(alpha=.15)
            if i==0:ax.set_title(c,fontsize=11,fontweight='bold')
            if j==0:ax.set_ylabel(s['id'],fontsize=7)
            if i==n-1:ax.set_xlabel('Origin-relative time (s)')
    ax=fig.add_subplot(gs[:max(1,n//2),3]);ax.set_aspect('equal');ax.set_xlim(-1.1,1.1);ax.set_ylim(-1.1,1.1)
    ax.add_collection(beach(ned_to_rtp(M),xy=(0,0),width=2));ax.axis('off');ax.set_title('Moment tensor')
    ax=fig.add_subplot(gs[max(1,n//2):,3]);ax.axis('off');ax.text(0,.95,'NED tensor (N m):\n'+np.array2string(M,precision=2)+'\n\n'
       +f'Stations: {len(accepted)}\nMean VR: {summary["mean_VR_percent"]:.1f}%\nCondition: {cond:.2g}\n\n'
       +'PyFK LAYERED FULL WAVEFORM',va='top',fontsize=9)
    fig.legend(*fig.axes[0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.42,1.005))
    fig.suptitle('TexNet moment tensor | '+args.physical_output+' | PyFK layered GFs',fontsize=15,fontweight='bold',y=1.025)
    fig.savefig(out/'moment_tensor_3c_fits.png',dpi=200,bbox_inches='tight')
    fig.savefig(out/'moment_tensor_3c_fits.pdf',bbox_inches='tight')
    if args.show:plt.show()
    plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
