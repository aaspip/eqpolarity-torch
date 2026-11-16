#!/usr/bin/env python3
"""TexNet full-MT experimental inversion. Uses EXACT SAME LOCAL QuakeML, miniSEED,
station CSV defaults and station/pick matching functions as the supplied
07_texnet_eqpolarity_focal_mechanism script. Does NOT download waveforms:
the supplied polarity script reads pre-downloaded miniSEED. The only online
request here is optional station instrument-response metadata for physical units.

WARNING: homogeneous full-space analytic elastodynamics with PB1D effective
parameters, NOT an independent layered FK kernel or publication-validated MT.

# Independent research solver; pyfk is NOT required.

python 07_texnet_moment_tensor_standalone.py   --physical-output DISP   --texnet-band 15-30   --dt 0.5   --fit-phase all   --fit-components 3C   --duration 1.0   --pre 45   --post 120   --tensor-type deviatoric   --min-stations 6   --min-snr 1.5   --snr-noise-seconds 20   --snr-signal-seconds 40   --min-noise-seconds 10   --station-shift-max 4   --station-shift-step 0.5   --station-shift-iterations 2   --max-station-peak 0   --experimental-fk   --independent-nk 32   --independent-naz 12   --independent-kmax-factor 2.5   --output-dir texnet2022wmmd_MT_standalone   --show
  
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

# -----------------------------------------------------------------------------
# Independent layered elastodynamics foundation (stage 1).
# Pure Python / NumPy / SciPy; no PyFK imports or bundled FK source.
# This is a verified state-propagation foundation, NOT YET the complete
# frequency-wavenumber Green-function quadrature.
# -----------------------------------------------------------------------------

def _elastic_layer_state_matrix(omega, k, vp, vs, density, qp=np.inf, qs=np.inf):
    """First-order depth ODE for coupled P-SV and decoupled SH waves.

    State = [u_x, u_z, tau_xz, tau_zz, u_y, tau_yz], with z positive
    downward, exp(i*k*x-i*omega*t). Tractions are on positive-z planes.
    Units: m, Pa; k rad/m, omega rad/s, speeds m/s, density kg/m^3.
    Complex moduli use constant-Q first-order approximation for omega>0.
    """
    if min(vp,vs,density) <= 0 or vp <= vs or omega <= 0 or k < 0:
        raise ValueError('Invalid layer parameters or spectral coordinates')
    # Negative imaginary part of moduli corresponds to passive attenuation
    # with exp(-i*omega*t) convention.
    mu = density * vs**2 * (1-1j/qs if np.isfinite(qs) else 1)
    lam2mu = density * vp**2 * (1-1j/qp if np.isfinite(qp) else 1)
    lam = lam2mu - 2*mu
    A=np.zeros((6,6),dtype=complex)
    # du_x/dz = tau_xz/mu - i*k*u_z
    A[0,1]=-1j*k; A[0,2]=1/mu
    # du_z/dz = (tau_zz - lam*i*k*u_x)/(lam+2mu)
    A[1,0]=-1j*k*lam/lam2mu; A[1,3]=1/lam2mu
    # d tau_xz/dz = -rho*omega^2*u_x - i*k*tau_xx
    # tau_xx = 4mu(lam+mu)/(lam+2mu)*i*k*u_x + lam/(lam+2mu)*tau_zz
    A[2,0]=4*mu*(lam+mu)/lam2mu*k*k-density*omega*omega
    A[2,3]=-1j*k*lam/lam2mu
    # d tau_zz/dz = -rho*omega^2*u_z - i*k*tau_xz
    A[3,1]=-density*omega*omega; A[3,2]=-1j*k
    # SH: du_y/dz=tau_yz/mu; d tau_yz/dz=(mu*k^2-rho*w^2)u_y
    A[4,5]=1/mu; A[5,4]=mu*k*k-density*omega*omega
    return A


def _layer_transfer_matrix(omega, k, thickness_m, vp, vs, density,
                           qp=np.inf, qs=np.inf):
    """Exact homogeneous-layer transfer via matrix exponential.

    For large evanescent exponents, this direct transfer representation
    becomes ill-conditioned; the completed solver must use a stabilized
    reflection/impedance recursion instead of multiplying these matrices.
    """
    from scipy.linalg import expm
    if thickness_m < 0:
        raise ValueError('Negative layer thickness')
    return expm(_elastic_layer_state_matrix(omega,k,vp,vs,density,qp,qs)*thickness_m)


def _test_independent_layer_foundation():
    """Local algebraic tests: zero thickness, composition, eigenvalues."""
    from scipy.linalg import eigvals
    vp,vs,rho=5500.,3100.,2600.
    omega,k=2*np.pi*.08,2*np.pi*.08/7000.
    A=_elastic_layer_state_matrix(omega,k,vp,vs,rho)
    expected=np.r_[1j*np.sqrt((omega/vp)**2-k*k+0j),
                   -1j*np.sqrt((omega/vp)**2-k*k+0j),
                   np.repeat(1j*np.sqrt((omega/vs)**2-k*k+0j),2),
                   np.repeat(-1j*np.sqrt((omega/vs)**2-k*k+0j),2)]
    assert all(np.min(np.abs(eigvals(A)-e)) < 1e-9 for e in expected)
    assert np.allclose(_layer_transfer_matrix(omega,k,0,vp,vs,rho),np.eye(6))
    t1=_layer_transfer_matrix(omega,k,1200,vp,vs,rho)
    t2=_layer_transfer_matrix(omega,k,800,vp,vs,rho)
    assert np.allclose(t2@t1,_layer_transfer_matrix(omega,k,2000,vp,vs,rho),rtol=1e-8,atol=1e-8)
    return True


# REVISION: SH outgoing impedance now uses complex shear modulus.
def _outgoing_halfspace_impedance(omega, k, vp, vs, density,
                                  qp=np.inf, qs=np.inf):
    """Traction/displacement impedance of outgoing waves in bottom half-space.

    Select eigenmodes with positive downward energy propagation (propagating)
    or exponential decay with depth (evanescent). State uses exp(-i omega t).
    Returns the P-SV 2x2 impedance and SH scalar impedance.
    """
    from scipy.linalg import eig
    A=_elastic_layer_state_matrix(omega,k,vp,vs,density,qp,qs)
    # Work with independently decoupled blocks, avoiding degeneracies at k=0.
    ps=A[np.ix_([0,1,2,3],[0,1,2,3])]
    vals,vecs=eig(ps)
    # With exp(i*k*x-i*omega*t), downward traveling modes have Im(q)>0;
    # evanescent modes decay for Re(q)<0. Avoid eigenvector flux tests:
    # normalized eigenvectors make flux tiny and numerically unreliable.
    selected=[j for j,q in enumerate(vals)
              if (np.real(q)<-1e-8*max(abs(q),1e-10) or
                  (abs(np.real(q))<=1e-8*max(abs(q),1e-10) and np.imag(q)>0))]
    if len(selected)!=2:
        raise RuntimeError(f'Cannot isolate two outgoing P-SV modes: {vals}')
    U=vecs[:2,selected];T=vecs[2:,selected]
    Z=T@np.linalg.inv(U)
    mu=density*vs**2*(1-1j/qs if np.isfinite(qs) else 1)
    # Use the same complex shear modulus as the SH state equation.
    # Using the real Vs here incorrectly removes attenuation from the
    # outgoing half-space radiation condition.
    qsh=np.sqrt(density*omega**2/mu-k*k+0j)
    if np.imag(qsh)<0 or (abs(np.imag(qsh))<1e-14 and np.real(qsh)<0):
        qsh=-qsh
    zsh=1j*mu*qsh
    return Z,zsh


def _impedance_layer_step(Zbottom, omega, k, thickness_m, vp, vs, density,
                          qp=np.inf, qs=np.inf, max_exponent=1.0):
    """Move the bottom radiation impedance to the top of a finite layer.

    Subdivide until each transfer exponential is moderate. Each fractional
    transform solves (T21+T22 Ztop)=(Zbottom)(T11+T12 Ztop).
    Unlike multiplying transfer matrices over the full stack, this keeps
    only local transfers. It is not a fully stabilized scattering recursion.
    """
    from scipy.linalg import expm, solve
    if thickness_m<0:raise ValueError('Negative thickness')
    if thickness_m==0:return Zbottom.copy()
    A=_elastic_layer_state_matrix(omega,k,vp,vs,density,qp,qs)
    ids=[0,1,2,3] if Zbottom.shape==(2,2) else [4,5]
    B=A[np.ix_(ids,ids)]
    n=max(1,int(np.ceil(thickness_m*max(abs(np.linalg.eigvals(B)))/max_exponent)))
    if n>100000:raise ValueError('Excessively fine layer subdivision')
    E=expm(B*(thickness_m/n))
    m=Zbottom.shape[0]
    e11,e12,e21,e22=E[:m,:m],E[:m,m:],E[m:,:m],E[m:,m:]
    Z=Zbottom.copy()
    for _ in range(n):
        # Ztop = (E22 - Zbottom E12)^-1 (Zbottom E11 - E21)
        Z=solve(e22-Z@e12,Z@e11-e21,assume_a='gen')
    return Z


def _pb1d_surface_impedance(omega,k,model=PB):
    """Bottom outgoing-radiation impedance propagated up to the free surface.

    Model rows are depth(km), Vp/Vs(km/s), density(g/cm3), Qp/Qs.
    Surface begins at depth 0; last row is the bottom half-space.
    """
    layers=np.asarray(model,float)
    layers=layers[layers[:,0]>=0]
    if len(layers)<1 or layers[0,0]!=0 or np.any(np.diff(layers[:,0])<=0):
        raise ValueError('Model must start at zero with strictly increasing depths')
    v=layers[-1]
    Z,sh=_outgoing_halfspace_impedance(omega,k,v[1]*1000,v[2]*1000,
                                       v[3]*1000,v[4],v[5])
    for i in range(len(layers)-2,-1,-1):
        a=layers[i];dz=(layers[i+1,0]-a[0])*1000
        Z=_impedance_layer_step(Z,omega,k,dz,a[1]*1000,a[2]*1000,
                                a[3]*1000,a[4],a[5])
        shmat=_impedance_layer_step(np.array([[sh]],complex),omega,k,dz,
                                    a[1]*1000,a[2]*1000,a[3]*1000,a[4],a[5])
        sh=shmat[0,0]
    return Z,sh


def _test_halfspace_boundary_conditions():
    """Verify homogeneous impedance and finite-layer recursion consistency."""
    from scipy.linalg import eig
    w=2*np.pi*.1; vp=5500.;vs=3100.;rho=2600.
    for k in [0.,w/7000.,w/2000.]:
        Z,sh=_outgoing_halfspace_impedance(w,k,vp,vs,rho)
        assert np.isfinite(Z).all() and np.isfinite(sh)
        Z2=_impedance_layer_step(Z,w,k,300.,vp,vs,rho)
        assert np.allclose(Z2,Z,rtol=2e-5,atol=1e-5), (k,Z,Z2)
        sh2=_impedance_layer_step(np.array([[sh]]),w,k,300.,vp,vs,rho)[0,0]
        assert np.allclose(sh2,sh,rtol=2e-5,atol=1e-5)
    return True


def _moment_tensor_spectral_jumps(moment_ned, omega, k, vp, vs, density,
                                  qp=np.inf, qs=np.inf):
    """Exact distributional source jumps for a point moment in a 2-D Fourier slice.

    Coordinates: x horizontal toward the chosen wavenumber, y transverse,
    z downward; exp(i*k*x-i*omega*t). Input M in this *local* x/y/z
    frame, SI N m. Fourier transform is over horizontal x and y, so the
    jump has units consistent with a 2-D horizontal spectral Green function.
    State ordering: [ux,uz,txz,tzz,uy,tyz]. The jump is state(below) -
    state(above). It is derived from f_i=-M_ij partial_j delta and
    explicitly removes singular stress terms from regular tractions.
    """
    M=np.asarray(moment_ned,dtype=complex)
    if M.shape!=(3,3) or not np.allclose(M,M.T,rtol=1e-12,atol=1e-12):
        raise ValueError('Moment tensor must be symmetric 3x3')
    mu=density*vs**2*(1-1j/qs if np.isfinite(qs) else 1)
    L=density*vp**2*(1-1j/qp if np.isfinite(qp) else 1)
    lam=L-2*mu
    return np.array([M[0,2]/mu, M[2,2]/L,
                     1j*k*(M[0,0]-lam/L*M[2,2]), 0j,
                     M[1,2]/mu, 1j*k*M[1,0]],dtype=complex)


def _source_layer_index(depth_m, model=PB):
    layers=np.asarray(model,float)
    layers=layers[layers[:,0]>=0]
    z=layers[:,0]*1000
    if depth_m<=0 or depth_m>=z[-1]:
        raise ValueError('Source must be below surface and above last model depth')
    return layers, int(np.searchsorted(z,depth_m,side='right')-1)


def _spectral_surface_response(omega,k,source_depth_m,moment_local,model=PB):
    """Surface displacement at one (omega,k) for a buried moment source.

    Uses a free surface and outgoing lower half-space, with source jumps
    at depth. This is a 2-D Cartesian horizontal Fourier *slice*, not yet
    an axisymmetric or 2-D inverse-horizontal-Fourier Green function.
    Do not interpret its output as a time-domain seismogram.
    """
    from scipy.linalg import solve
    layers,si=_source_layer_index(source_depth_m,model)
    depths=layers[:,0]*1000
    layer=layers[si]
    J=_moment_tensor_spectral_jumps(moment_local,omega,k,
            layer[1]*1000,layer[2]*1000,layer[3]*1000,layer[4],layer[5])
    # Free-surface basis at source-minus: propagate [u,0] downward.
    T=np.eye(6,dtype=complex)
    for i in range(si+1):
        top=depths[i]
        bottom=source_depth_m if i==si else depths[i+1]
        if bottom>top:
            a=layers[i]
            T=_layer_transfer_matrix(omega,k,bottom-top,
                 a[1]*1000,a[2]*1000,a[3]*1000,a[4],a[5])@T
    # Outgoing impedance at source-plus, from bottom halfspace upward.
    a=layers[-1]
    Z,sh=_outgoing_halfspace_impedance(omega,k,a[1]*1000,a[2]*1000,
                                      a[3]*1000,a[4],a[5])
    for i in range(len(layers)-2,si-1,-1):
        a=layers[i]
        top=source_depth_m if i==si else depths[i]
        dz=depths[i+1]-top
        if dz>0:
            Z=_impedance_layer_step(Z,omega,k,dz,a[1]*1000,a[2]*1000,
                                     a[3]*1000,a[4],a[5])
            sh=_impedance_layer_step(np.array([[sh]],complex),omega,k,dz,
                                     a[1]*1000,a[2]*1000,a[3]*1000,a[4],a[5])[0,0]
    # P-SV state [ux,uz,txz,tzz]; SH [uy,tyz].
    Tp=T[np.ix_([0,1,2,3],[0,1])]
    A,C=Tp[:2,:],Tp[2:,:]
    u_ps=solve(C-Z@A,Z@J[:2]-J[2:4])
    ush=solve(np.array([[T[5,4]-sh*T[4,4]]]),
              np.array([sh*J[4]-J[5]]))[0]
    return np.array([u_ps[0],ush,u_ps[1]],dtype=complex)


def _test_moment_source_jumps():
    """Verify linearity, pure DC symmetry and free-surface source matching."""
    w=2*np.pi*.08;k=w/6500;d=3500.
    tensors=[]
    for B in BASIS:tensors.append(B.astype(float))
    for B in tensors:
        a=_spectral_surface_response(w,k,d,B)
        b=_spectral_surface_response(w,k,d,2*B)
        assert np.isfinite(a).all() and np.allclose(b,2*a,rtol=1e-9,atol=1e-15)
    # SH cannot be excited by a pure Mxx or Mzz source for ky=0.
    for j in (0,2):
        r=_spectral_surface_response(w,k,d,BASIS[j])
        assert abs(r[1])<1e-12*max(1,abs(r[0]),abs(r[2]))
    return True


def _horizontal_fourier_azimuth_integral(omega, k, radius_m, azimuth_deg,
                                          depth_m, moment_ned, model=PB,
                                          n_azimuth=24):
    """Analytically integrate the horizontal Fourier azimuth via Bessel modes.

    The plane-wave elastic response for a symmetric moment tensor is a finite
    trigonometric polynomial (orders |m|<=3). Its angular Fourier coefficients
    are obtained by a discrete Fourier transform; the oscillatory receiver
    phase is integrated exactly using the Jacobi-Anger identity. Unlike direct
    angular quadrature this does not alias when k*receiver_distance is large.
    """
    from scipy.special import jv
    if n_azimuth < 8 or n_azimuth % 2:
        raise ValueError('Use an even azimuthal count >= 8')
    if radius_m < 0 or k < 0 or omega <= 0:
        raise ValueError('Invalid spectral coordinates')
    M=np.asarray(moment_ned,float)
    if M.shape!=(3,3) or not np.allclose(M,M.T):
        raise ValueError('Expected symmetric NED moment tensor')
    phi=2*np.pi*np.arange(n_azimuth)/n_azimuth
    values=np.empty((n_azimuth,3),complex)
    for i,angle in enumerate(phi):
        ca,sa=np.cos(angle),np.sin(angle)
        R=np.array([[ca,-sa,0.],[sa,ca,0.],[0.,0.,1.]])
        values[i]=R@_spectral_surface_response(
            omega,k,depth_m,R.T@M@R,model)
    coefficients=np.fft.fft(values,axis=0)/n_azimuth
    m=np.rint(np.fft.fftfreq(n_azimuth)*n_azimuth).astype(int)
    az=np.deg2rad(azimuth_deg)
    factors=(1j)**m*jv(m,k*radius_m)*np.exp(1j*m*az)
    return 2*np.pi*np.einsum('m,mc->c',factors,coefficients)


def _test_angular_bessel_identity():
    """Check exact angular integration against a high-resolution direct sum."""
    from scipy.special import jv
    for kr in [0., 2., 40., 250.]:
        for m in range(-3,4):
            az=.37
            angles=np.arange(32768)*2*np.pi/32768
            numerical=np.mean(np.exp(1j*m*angles+1j*kr*np.cos(angles-az)))*2*np.pi
            analytic=2*np.pi*(1j)**m*jv(m,kr)*np.exp(1j*m*az)
            assert abs(numerical-analytic)<1e-11,(kr,m,numerical,analytic)
    return True


def _radial_inverse_fourier_spectrum(omega, radius_m, azimuth_deg,
                                     depth_m, moment_ned, k_grid,
                                     model=PB, n_azimuth=24):
    """Experimental radial quadrature for one frequency, not PyFK parity.

    Integrates k dk/(2*pi)^2 with a trapezoid rule.  This straightforward
    Cartesian Fourier inversion is expensive and can be unstable near
    Rayleigh poles or high-k evanescence.  The completed solver requires
    contour deformation, integration convergence tests, and time synthesis.
    """
    k_grid=np.asarray(k_grid,float)
    if k_grid.ndim!=1 or len(k_grid)<3 or k_grid[0]<0 or np.any(np.diff(k_grid)<=0):
        raise ValueError('k_grid must be strictly increasing and nonnegative')
    angular=[]
    for k in k_grid:
        angular.append(_horizontal_fourier_azimuth_integral(
            omega,float(k),radius_m,azimuth_deg,depth_m,moment_ned,
            model,n_azimuth))
    return np.trapz(np.asarray(angular)*k_grid[:,None],k_grid,axis=0)/(2*np.pi)**2


def _test_angular_fourier_covariance():
    """A rotated source and receiver must yield a rotated displacement."""
    w=2*np.pi*.07;k=w/6500.;r=12000.;depth=3500.
    M=np.array([[1.,.4,.2],[.4,-.6,-.3],[.2,-.3,-.4]])
    theta=np.deg2rad(30.)
    Q=np.array([[np.cos(theta),-np.sin(theta),0.],
                [np.sin(theta),np.cos(theta),0.],[0.,0.,1.]])
    u=_horizontal_fourier_azimuth_integral(w,k,r,15.,depth,M,n_azimuth=12)
    v=_horizontal_fourier_azimuth_integral(w,k,r,45.,depth,Q@M@Q.T,n_azimuth=12)
    assert np.allclose(v,Q@u,rtol=1e-6,atol=1e-22),(u,v)
    return True



def _real_spectrum_to_time(positive_frequency_spectrum, dt, npts,
                           first_sample_s=0.0, quantity='DISP'):
    """Invert a causal, real-valued displacement spectrum to time samples.

    Input F(f) is the continuous Fourier transform under
    F(f)=integral u(t) exp(-2*pi*i*f*t) dt.  This routine uses the
    inverse transform u(t)=integral F(f) exp(+2*pi*i*f*t) df.
    The supplied frequencies must be exactly np.fft.rfftfreq(npts, dt).
    A nonzero first_sample_s shifts the output sample origin; it is NOT
    a change in the physical origin time of the source.

    The DC and Nyquist bins must be real for a real time series.
    Input shape is (npts//2+1, ...) and output is (npts, ...).
    """
    if dt <= 0 or npts < 4 or not isinstance(npts, (int, np.integer)):
        raise ValueError('Invalid FFT time grid')
    F=np.asarray(positive_frequency_spectrum, complex)
    if F.shape[0] != npts//2+1:
        raise ValueError('Spectrum does not match the requested FFT grid')
    if not np.isfinite(F).all():
        raise ValueError('Nonfinite frequency-domain Green function')
    freqs=np.fft.rfftfreq(npts, dt)
    phase=np.exp(2j*np.pi*freqs*first_sample_s)
    phase=phase.reshape((len(freqs),)+(1,)*(F.ndim-1))
    shifted=F*phase
    if quantity == 'VEL':
        shifted=shifted*(2j*np.pi*freqs).reshape((-1,)+(1,)*(F.ndim-1))
    elif quantity != 'DISP':
        raise ValueError('quantity must be DISP or VEL')
    # Nyquist frequency has no conjugate partner: its imaginary part
    # cannot be represented by a real-valued sampled signal.
    shifted=shifted.copy()
    shifted[0]=shifted[0].real
    if npts % 2 == 0:
        shifted[-1]=shifted[-1].real
    return np.fft.irfft(shifted, n=npts, axis=0)/dt


def _causal_gaussian_stf_spectrum(dt, npts, duration):
    """Fourier transform of the original script's sampled causal STF.

    Preserves the discrete source-history normalization used by the
    previous PyFK adapter: sum(rate) == 1 (not sum(rate)*dt == 1).
    The transform is dimensionless and is suitable for multiplying a
    continuous-transform Green function, since the discrete weights
    approximate the source-time integral.
    """
    if duration <= 0 or dt <= 0:
        raise ValueError('Duration and sampling must be positive')
    t=np.arange(max(3,int(np.ceil(duration*5/dt))))*dt
    sigma=max(duration/2.355,dt)
    rate=np.exp(-.5*((t-2*sigma)/sigma)**2)
    rate/=rate.sum()
    padded=np.zeros(npts)
    if len(rate)>npts:
        raise ValueError('FFT length is shorter than source time function')
    padded[:len(rate)]=rate
    return np.fft.rfft(padded)


def _test_time_reconstruction():
    """FFT convention, scaling, source normalization and shift checks."""
    dt=.25;n=256
    t=np.arange(n)*dt
    f0=0.125
    x=np.cos(2*np.pi*f0*t)
    F=np.fft.rfft(x)*dt
    y=_real_spectrum_to_time(F,dt,n)
    assert np.allclose(x,y,atol=1e-12)
    shifted=_real_spectrum_to_time(F,dt,n,first_sample_s=2.0)
    assert np.allclose(shifted,np.cos(2*np.pi*f0*(t+2)),atol=1e-12)
    vel=_real_spectrum_to_time(F,dt,n,quantity='VEL')
    assert np.allclose(vel,-2*np.pi*f0*np.sin(2*np.pi*f0*t),atol=1e-12)
    stf=_causal_gaussian_stf_spectrum(dt,n,1.0)
    assert np.isclose(stf[0],1.,atol=1e-12)
    assert np.isfinite(stf).all()
    return True


def _experimental_fk_frequency_spectrum(freq_hz, distance_km, azimuth_deg,
                                        depth_m, moment_ned, nk=48, naz=16,
                                        kmax_factor=2.5):
    """Experimental full 2-D horizontal inverse-Fourier quadrature.

    This is *not* a validated PyFK-equivalent solver. The radial cutoff is
    kmax_factor * omega / min(Vs), and both radial and angular convergence
    must be established before any scientific interpretation.
    """
    if freq_hz <= 0:
        return np.zeros(3, dtype=complex)
    if nk < 8 or naz < 8 or naz % 2:
        raise ValueError('nk >= 8 and even naz >= 8 required')
    layers=PB[PB[:,0]>=0]
    kmax=kmax_factor*2*np.pi*freq_hz/(1000*np.min(layers[:,2]))
    # Midpoint quadrature avoids the k=0 degenerate eigenvectors.
    dk=kmax/nk
    kgrid=(np.arange(nk)+.5)*dk
    vals=np.empty((nk,3),complex)
    for i,k in enumerate(kgrid):
        vals[i]=_horizontal_fourier_azimuth_integral(
            2*np.pi*freq_hz,float(k),distance_km*1000,
            azimuth_deg,depth_m,moment_ned,n_azimuth=naz)
    return np.sum(vals*kgrid[:,None],axis=0)*dk/(2*np.pi)**2


def _experimental_fk_convergence(freq_hz, distance_km, azimuth_deg,
                                 depth_m, moment_ned, nk=24, naz=12):
    """Compare successive radial/angular quadrature refinements.

    Return a relative complex-spectrum discrepancy, not a proof of accuracy.
    """
    coarse=_experimental_fk_frequency_spectrum(
        freq_hz,distance_km,azimuth_deg,depth_m,moment_ned,nk,naz)
    fine=_experimental_fk_frequency_spectrum(
        freq_hz,distance_km,azimuth_deg,depth_m,moment_ned,2*nk,2*naz)
    error=np.linalg.norm(fine-coarse)/max(np.linalg.norm(fine),1e-30)
    return coarse,fine,float(error)


def build_independent_fk_kernels(stations, args, origin):
    """Generate experimental time-domain FK basis, with explicit opt-in.

    No PyFK is imported. This route is computationally expensive and has NOT
    passed strict-parity tests. It is disabled by default to avoid presenting
    unvalidated source mechanisms as scientifically reliable.
    """
    _test_independent_layer_foundation()
    _test_halfspace_boundary_conditions()
    _test_moment_source_jumps()
    _test_angular_fourier_covariance()
    _test_angular_bessel_identity()
    _test_time_reconstruction()
    if not args.experimental_fk:
        raise RuntimeError(
            'Independent spectral FK components and a numerical synthesis '
            'path are available, but PyFK waveform parity is not established. '
            'To test the unvalidated implementation explicitly, supply '
            '--experimental-fk. Do not interpret its moment tensors as validated.')
    warnings.warn('EXPERIMENTAL FK: waveform amplitudes, phase and numerical '
                  'convergence are NOT validated against PyFK.', RuntimeWarning)
    npt=int(2**np.ceil(np.log2(max(512,(args.pre+args.post+80)/args.dt))))
    freqs=np.fft.rfftfreq(npt,args.dt)
    # Do not silently treat uncomputed frequencies as physically zero.
    # The partial-band approximation remains experimental, and cannot
    # reproduce the time-domain filtering of complete PyFK waveforms.
    fmin=max(0.001,args.low*0.45)
    fmax=min(.5/args.dt,args.high*1.8)
    active=np.where((freqs>=fmin)&(freqs<=fmax))[0]
    stf=_causal_gaussian_stf_spectrum(args.dt,npt,args.duration)
    ref_moment=1e15
    for si,st in enumerate(stations):
        spec=np.zeros((len(freqs),3,6),complex)
        print(f'Experimental independent FK: station {si+1}/{len(stations)} '
              f"{st['id']}, {len(active)} frequencies",flush=True)
        for fi in active:
            for j,B in enumerate(BASIS):
                spec[fi,:,j]=_experimental_fk_frequency_spectrum(
                    freqs[fi],st['distance_km'],st['azimuth'],
                    float(origin.depth),ref_moment*B,
                    nk=args.independent_nk,naz=args.independent_naz,
                    kmax_factor=args.independent_kmax_factor)*stf[fi]
        # Frequency-domain response is in displacement per reference moment.
        # No additional cm-to-m conversion: SI is used throughout.
        # Match the original PyFK adapter's pre-arrival time origin.
        # The FFT window starts before the earliest direct arrival, avoiding
        # circular wrapping of causal waveforms at the origin.
        predicted_p=layered_ray(float(origin.depth)/1000,
                                st['distance_km'],'P')[0]
        b=float(predicted_p-12.0)
        displacement=_real_spectrum_to_time(spec,args.dt,npt,
                                             first_sample_s=b,
                                             quantity=args.physical_output)
        displacement=bandpass(displacement,args.dt,args.low,args.high)
        st['fk_basis']=displacement/ref_moment
        st['fk_start_s']=b
        if not np.isfinite(st['fk_basis']).all():
            raise RuntimeError(f'Nonfinite experimental FK kernel at {st["id"]}')
    print('WARNING: experimental FK generated; no PyFK parity claim.',flush=True)


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
    p.add_argument('--experimental-fk',action='store_true',help='Allow unvalidated independent FK synthesis (research diagnostics only)')
    p.add_argument('--independent-nk',type=int,default=32,help='Radial midpoint quadrature nodes (experimental)')
    p.add_argument('--independent-naz',type=int,default=12,help='Even angular quadrature nodes (experimental)')
    p.add_argument('--independent-kmax-factor',type=float,default=2.5,help='Wavenumber cutoff relative to omega/min(Vs)')
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
        G=np.zeros((len(y),3,6),dtype=float)  # Independent FK basis computed after station QC
        # Optionally fit only a short P window; full 3C fitting is supported by independent FK solver.
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
    build_independent_fk_kernels(accepted, args, origin)
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
    if final_vr < 10:
        warnings.warn(
            f'Independent FK forward model has global VR={final_vr:.2f}% '
            '(<10%). The estimated moment tensor is NOT validated; '
            'check waveform timing, radial quadrature, source normalization '
            'and PyFK Green-function parity before interpreting it.',
            RuntimeWarning)
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
                 fit_components=args.fit_components, source_duration_s=args.duration, frequency_band_hz=[args.low,args.high], sampling_interval_s=args.dt, texnet_band=args.texnet_band, method='EXPERIMENTAL UNVALIDATED pure-Python layered spectral FK quadrature, PB1D model',tensor_NED_Nm=M.tolist(),
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
