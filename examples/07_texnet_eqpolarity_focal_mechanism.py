#!/usr/bin/env python3
"""
End-to-end TexNet focal-mechanism workflow using EQPolarity-Torch + PyHASH.

Workflow
--------
1. Read one QuakeML event and its P arrivals.
2. Read the corresponding miniSEED waveform file.
3. Match each P pick to a vertical-component trace.
4. Cut a 600-sample window centered on the P arrival.
5. Reproduce the historical eqp.py preprocessing (linear detrend, 1--20 Hz,
   P at sample 299, max-abs normalization).
6. Predict first-motion polarity with the Texas EQPolarity model and, by
   default, reproduce the historical eqp.py -> HASH polarity mapping.
7. Match stations to the supplied TexNet station metadata CSV.
8. Compute source-receiver azimuth/distance from station metadata.
9. Convert QuakeML/TauP takeoff convention to HASH/SKHASH convention
   (critical: HASH uses <90° upgoing; QuakeML uses <90° downgoing).
10. Measure optional three-component S/P amplitude ratios using the legacy
    st2sac_psamp variance-energy method from the uploaded sac.py.
11. Convert EQPolarity probability to a signed HASH/PyHASH polarity weight.
12. Run PyHASH with polarity + S/P constraints and geometry Monte Carlo trials.
13. Save QC tables, waveform/polarity diagnostics, and a beachball figure.

The script is deliberately conservative:
- stations without metadata are skipped, not guessed;
- traces that do not cover the complete P window are skipped;
- gaps/masked samples are rejected;
- low-confidence polarity predictions can be excluded;
- duplicate station metadata are resolved using event-time validity;
- exact network/station/location/channel matches are attempted first;
- vertical-channel fallbacks are logged explicitly;
- insufficient focal-sphere coverage raises a clear diagnostic;
- every accepted/rejected pick and reason is written to CSV.

Requirements
------------
pip install obspy pandas numpy matplotlib torch h5py
pip install -e .

Example
-------
python examples/pyhash/07_texnet_eqpolarity_focal_mechanism.py

or explicitly:

python examples/pyhash/07_texnet_eqpolarity_focal_mechanism.py \
  --qml /Users/chenyk/DATALIB/TexNet-refined-database-catalog-PSpicks-EVENTS/texnet2020galz.qml \
  --mseed /Users/chenyk/DATALIB/TexNet-refined-database-catalog-PSpicks-WAVEFORMS/texnet2020galz.mseed \
  --stations /Users/chenyk/chenyk.data2/various/cyksmall/texnet_stations_2024_0209_extra.csv \
  --output-dir texnet2020galz_focal_mechanism \
  --model texas
  --show

Notes on geometry
-----------------
Geometry is resolved adaptively:
  azimuth : station metadata when available, otherwise QuakeML arrival azimuth
  takeoff : QuakeML arrival value when available; otherwise the origin earth
            model is used (standard TauP models such as iasp91, or PB1D).

The PB1D model supplied with this workflow is embedded below and is used only
when the QuakeML origin actually identifies a PB1D earth model.

EQPolarity convention
---------------------
EQPolarity-Torch:
    class 0 = Up
    class 1 = Down

The network output is P(Down).  PyHASH receives:
    +confidence = Up
    -confidence = Down

where confidence = abs(2 * P(Down) - 1).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# User-provided PB1D model
# -----------------------------------------------------------------------------

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

eid='texnet2020galz'
eid='texnet2021ynzp'
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


def require_runtime():
    """Import heavier dependencies with a useful error message."""
    missing = []
    try:
        from obspy import read, read_events  # noqa: F401
    except Exception:
        missing.append("obspy")
    try:
        import torch  # noqa: F401
    except Exception:
        missing.append("torch")
    try:
        import matplotlib  # noqa: F401
    except Exception:
        missing.append("matplotlib")

    if missing:
        raise RuntimeError(
            "Missing required package(s): "
            + ", ".join(missing)
            + "\nInstall, for example:\n"
              "  python -m pip install obspy matplotlib pandas numpy torch h5py\n"
              "and install this repository with:\n"
              "  python -m pip install -e ."
        )


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


def extract_p_observations(event, origin, use_zero_weight=False):
    """
    Link preferred-origin P arrivals back to QuakeML picks.

    Only arrivals in the selected origin are used. By default, arrivals whose
    origin time_weight is exactly zero are excluded because those phases were
    not used in the preferred-location solution.
    """
    pick_map = {str(p.resource_id): p for p in event.picks}
    out = []

    for arr in origin.arrivals:
        phase = (arr.phase or "").strip().upper()
        if not phase.startswith("P"):
            continue

        weight = as_float(arr.time_weight)
        if (not use_zero_weight) and np.isfinite(weight) and weight == 0.0:
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
        raise ValueError("No usable P arrivals were found in the selected origin.")

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


def choose_trace(stream, obs):
    """
    Find the best vertical trace for one QuakeML P pick.

    Exact NSLC match is preferred. Then progressively relax location/channel
    while still requiring the same network/station and a vertical component.
    """
    net, sta, loc, cha = (
        obs.network,
        obs.station,
        obs.location,
        obs.channel,
    )

    candidates = []

    def add(sel, rank, why):
        for tr in sel:
            key = tr.id
            candidates.append((rank, why, key, tr))

    # Exact seed code.
    if cha:
        add(
            stream.select(
                network=net or "*",
                station=sta,
                location=loc if loc else "*",
                channel=cha,
            ),
            0,
            "exact_nslc",
        )

    # Exact station + requested vertical family.
    if cha and cha.endswith("Z"):
        family = cha[:2] + "Z" if len(cha) >= 3 else "*Z"
        add(
            stream.select(
                network=net or "*",
                station=sta,
                location=loc if loc else "*",
                channel=family,
            ),
            1,
            "same_vertical_family",
        )

    # Any vertical component at exact network+station.
    add(
        stream.select(network=net or "*", station=sta, channel="*Z"),
        2,
        "any_vertical_same_network_station",
    )

    # Last-resort station-only vertical match.
    add(
        stream.select(station=sta, channel="*Z"),
        3,
        "station_only_vertical",
    )

    if not candidates:
        return None, "waveform_trace_not_found"

    # Deduplicate by trace identity while preserving best rank.
    best_by_id = {}
    for rank, why, key, tr in candidates:
        if key not in best_by_id or rank < best_by_id[key][0]:
            best_by_id[key] = (rank, why, tr)

    candidates = list(best_by_id.values())

    # Prefer traces containing the pick with margin, then lowest match rank,
    # then highest sampling rate.
    def score(item):
        rank, why, tr = item
        contains = tr.stats.starttime <= obs.pick_time <= tr.stats.endtime
        return (
            0 if contains else 1,
            rank,
            -float(tr.stats.sampling_rate),
            str(tr.id),
        )

    rank, why, tr = sorted(candidates, key=score)[0]

    if not (tr.stats.starttime <= obs.pick_time <= tr.stats.endtime):
        return None, "matched_trace_does_not_contain_pick"

    return tr, why


def extract_centered_window(
    tr,
    pick_time,
    target_sr=100.0,
    n_samples=600,
    detrend=True,
    *,
    freqmin=1.0,
    freqmax=20.0,
    legacy_eqp_preprocess=True,
):
    """
    Prepare the exact 600-sample EQPolarity input.

    By default this intentionally reproduces the preprocessing in the user's
    historical ``eqp.py`` implementation:

      * resample to 100 Hz with ObsPy ``Trace.resample`` when necessary;
      * linear detrend;
      * bandpass 1--20 Hz;
      * trim from P-3+0.01 s through P+3 s;
      * require exactly 600 samples;
      * normalize by max(abs(data)).

    The +0.01 s offset is important: at 100 Hz it places P at sample 299
    (zero based), matching the legacy implementation rather than sample 300.

    A non-legacy branch remains available for experimentation.
    """
    if n_samples != 600:
        raise ValueError(
            "The packaged EQPolarity model expects exactly 600 samples."
        )

    x = tr.copy()

    if legacy_eqp_preprocess:
        # Legacy eqp.py:
        #   if sampling_rate != 100: st.resample(100)
        #   st.detrend(type='linear')
        #   st.filter(type='bandpass', freqmin=1, freqmax=20)
        #   st.trim(P-3+0.01, P+3)
        if abs(float(x.stats.sampling_rate) - float(target_sr)) > 1e-8:
            x.resample(float(target_sr))

        if detrend:
            x.detrend(type="linear")

        nyq = 0.5 * float(x.stats.sampling_rate)
        f2 = min(float(freqmax), 0.95 * nyq)
        f1 = float(freqmin)
        if not (0 < f1 < f2):
            raise ValueError(
                f"invalid_EQPolarity_bandpass:{f1:g}-{f2:g}_Hz"
            )

        x.filter(
            type="bandpass",
            freqmin=f1,
            freqmax=f2,
        )

        start = pick_time - 3.0 + 1.0 / float(target_sr)
        end = pick_time + 3.0

        # Do not pad: the historical code required len(dat)==600.
        if x.stats.starttime > start or x.stats.endtime < end:
            raise ValueError(
                "trace_does_not_cover_complete_legacy_600_sample_window"
            )

        x.trim(starttime=start, endtime=end, pad=False)
        data = np.asarray(x.data, dtype=np.float32)

        # Floating point trim edge behavior can occasionally leave 599/601
        # samples. Re-trim by nearest sample around the legacy P index.
        if data.size != n_samples:
            # Construct the intended window directly from the resampled trace.
            y = tr.copy()
            if abs(float(y.stats.sampling_rate) - float(target_sr)) > 1e-8:
                y.resample(float(target_sr))
            if detrend:
                y.detrend(type="linear")
            y.filter(type="bandpass", freqmin=f1, freqmax=f2)

            pidx = int(round((pick_time - y.stats.starttime) * target_sr))
            i0 = pidx - 299
            i1 = i0 + n_samples
            if i0 < 0 or i1 > len(y.data):
                raise ValueError(
                    "legacy_window_index_outside_trace"
                )
            data = np.asarray(y.data[i0:i1], dtype=np.float32)

    else:
        # More conventional centered interpolation branch.
        p_index = n_samples // 2
        start = pick_time - p_index / target_sr
        end = start + (n_samples - 1) / target_sr

        if x.stats.starttime > start or x.stats.endtime < end:
            raise ValueError(
                "trace_does_not_cover_complete_600_sample_window"
            )

        if detrend:
            x.detrend("demean")
            x.detrend("linear")

        if float(x.stats.sampling_rate) > 1.25 * target_sr:
            x.filter(
                "lowpass",
                freq=0.45 * target_sr,
                corners=4,
                zerophase=True,
            )

        x.interpolate(
            sampling_rate=target_sr,
            method="lanczos",
            a=20,
            starttime=start,
            npts=n_samples,
        )
        data = np.asarray(x.data, dtype=np.float32)

    if data.size != n_samples:
        raise ValueError(
            f"EQPolarity_preprocessing_returned_{data.size}_samples"
        )
    if np.ma.isMaskedArray(data) and np.ma.getmaskarray(data).any():
        raise ValueError("waveform_window_contains_gap")
    if not np.all(np.isfinite(data)):
        raise ValueError("waveform_contains_nonfinite_samples")

    amp = float(np.max(np.abs(data)))
    if not np.isfinite(amp) or amp <= 0:
        raise ValueError("zero_or_invalid_waveform_amplitude")

    data = data / amp
    return np.asarray(data, dtype=np.float32)



def manual_polarity_to_sign(value):
    s = str(value or "").strip().lower()
    if s in {"positive", "up", "+", "u"}:
        return 1.0
    if s in {"negative", "down", "-", "d"}:
        return -1.0
    return np.nan


def circular_difference_deg(a, b):
    if not (np.isfinite(a) and np.isfinite(b)):
        return np.nan
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _earth_model_name(origin):
    """Return a compact earth-model name from a QuakeML resource identifier."""
    if not getattr(origin, "earth_model_id", None):
        return ""
    s = str(origin.earth_model_id).strip()
    if "/" in s:
        s = s.rsplit("/", 1)[-1]
    return s.strip()


_TAUP_CACHE = {}


def _get_taup_model(name):
    """Cache ObsPy TauP models because model construction is relatively costly."""
    from obspy.taup import TauPyModel

    key = str(name).strip().lower()
    aliases = {
        "iasp91": "iasp91",
        "ak135": "ak135",
        "prem": "prem",
        "ak135f": "ak135f_no_mud",
        "ak135f_no_mud": "ak135f_no_mud",
    }
    model_name = aliases.get(key, key)

    if model_name not in _TAUP_CACHE:
        _TAUP_CACHE[model_name] = TauPyModel(model=model_name)

    return _TAUP_CACHE[model_name], model_name


def estimate_takeoff_taup(origin, obs, station_row):
    """
    Estimate a P-wave takeoff angle with ObsPy TauP.

    The returned angle follows the same convention used by SKHASH/PyHASH:
    < 90 degrees is upgoing and > 90 degrees is downgoing.

    For events whose QuakeML earth_model_id is a standard TauP model
    (e.g. iasp91), the arrival whose predicted travel time is closest to
    the observed P-pick travel time is preferred.
    """
    if station_row is None:
        return np.nan, "", np.nan, ""

    model_id = _earth_model_name(origin).lower()

    # Only map known standard models automatically.  A local model such as
    # PB1D must not silently be replaced by iasp91.
    known = {"iasp91", "ak135", "prem", "ak135f", "ak135f_no_mud"}
    if model_id not in known:
        return np.nan, "", np.nan, ""

    try:
        model, model_name = _get_taup_model(model_id)

        source_depth_km = max(0.0, as_float(origin.depth) / 1000.0)
        stalat = float(station_row["Latitude (WGS84)"])
        stalon = float(station_row["Longitude (WGS84)"])

        # First ask specifically for common P branches. Some local geometries
        # can be picky about phase naming, so fall back to ttbasic.
        arrivals = model.get_travel_times_geo(
            source_depth_in_km=source_depth_km,
            source_latitude_in_deg=float(origin.latitude),
            source_longitude_in_deg=float(origin.longitude),
            receiver_latitude_in_deg=stalat,
            receiver_longitude_in_deg=stalon,
            phase_list=["P", "p", "Pn"],
        )

        if not arrivals:
            arrivals = model.get_travel_times_geo(
                source_depth_in_km=source_depth_km,
                source_latitude_in_deg=float(origin.latitude),
                source_longitude_in_deg=float(origin.longitude),
                receiver_latitude_in_deg=stalat,
                receiver_longitude_in_deg=stalon,
                phase_list=["ttbasic"],
            )

        # Keep P-type phases only.
        p_arrivals = [
            a for a in arrivals
            if str(getattr(a, "name", "")).lower().startswith("p")
        ]
        if not p_arrivals:
            return np.nan, "", np.nan, ""

        observed_tt = as_float(obs.pick_time - origin.time)

        if np.isfinite(observed_tt):
            best = min(
                p_arrivals,
                key=lambda a: abs(float(a.time) - observed_tt),
            )
        else:
            best = min(p_arrivals, key=lambda a: float(a.time))

        # ObsPy TauP follows the QuakeML convention: <90 deg is
        # downgoing, >90 deg is upgoing. SKHASH/HASH uses the opposite
        # convention (<90 upgoing, >90 downgoing), so FLIP it here.
        angle_qml = as_float(best.takeoff_angle)
        if not (np.isfinite(angle_qml) and 0.0 < angle_qml <= 180.0):
            return np.nan, "", np.nan, ""

        angle_hash = 180.0 - angle_qml

        return (
            angle_hash,
            f"taup:{model_name}:{best.name}:flipped_to_HASH",
            float(best.time),
            str(best.name),
        )

    except Exception as exc:
        return np.nan, f"taup_failed:{type(exc).__name__}:{exc}", np.nan, ""


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


def estimate_takeoff_pb1d(origin, station_row, horizontal_distance_km):
    """
    Direct-P takeoff angle for the embedded PB1D model using flat-layer ray tracing.

    This solves Snell's-law ray parameter p for the direct upgoing P ray through
    the supplied 1-D Vp(z) model. It is intended as a robust fallback when a
    PB1D-based QuakeML origin lacks stored takeoff angles.

    Returns
    -------
    angle_deg, predicted_time_s
        SKHASH convention: upgoing rays are < 90 degrees.
    """
    if station_row is None or not np.isfinite(horizontal_distance_km):
        return np.nan, np.nan

    zsrc = as_float(origin.depth) / 1000.0
    if not np.isfinite(zsrc) or zsrc <= 0:
        return np.nan, np.nan

    elev_m = as_float(station_row.get("Elevation", 0.0), default=0.0)
    zrec = -elev_m / 1000.0 if np.isfinite(elev_m) else 0.0

    # Ensure path is ordered from receiver depth to source depth.
    z0, z1 = sorted([zrec, zsrc])
    if z1 - z0 < 1e-5:
        return np.nan, np.nan

    depths, vp_nodes = _parse_pb1d_vp()

    # Fine integration grid; linear interpolation is adequate for this fallback.
    dz = min(0.02, max(0.002, (z1 - z0) / 2000.0))
    n = max(50, int(np.ceil((z1 - z0) / dz)) + 1)
    z = np.linspace(z0, z1, n)
    vp = np.interp(z, depths, vp_nodes)
    if not np.all(np.isfinite(vp)) or np.any(vp <= 0):
        return np.nan, np.nan

    x_target = max(0.0, float(horizontal_distance_km))

    def x_and_t(p):
        pv = p * vp
        if np.any(pv >= 1.0):
            return np.inf, np.inf
        cosi = np.sqrt(np.maximum(1.0 - pv * pv, 1e-14))
        tan_i = pv / cosi
        sec_over_v = 1.0 / (vp * cosi)
        x = np.trapz(tan_i, z)
        t = np.trapz(sec_over_v, z)
        return float(x), float(t)

    # p < 1/v everywhere along the ray.
    p_lo = 0.0
    p_hi = 0.999999 / float(np.max(vp))

    x_hi, _ = x_and_t(p_hi)
    if not np.isfinite(x_hi) or x_target > x_hi:
        return np.nan, np.nan

    for _ in range(80):
        p_mid = 0.5 * (p_lo + p_hi)
        x_mid, _ = x_and_t(p_mid)
        if x_mid < x_target:
            p_lo = p_mid
        else:
            p_hi = p_mid

    p = 0.5 * (p_lo + p_hi)
    _, t_pred = x_and_t(p)

    vsrc = float(np.interp(zsrc, depths, vp_nodes))
    s = np.clip(p * vsrc, 0.0, 1.0)
    angle = float(np.degrees(np.arcsin(s)))  # upgoing, therefore <90

    if not (0.0 <= angle < 90.0):
        return np.nan, np.nan

    return angle, t_pred


def resolve_takeoff_angle(origin, obs, station_row, distance_km):
    """
    Resolve takeoff angle using the best available source.

    Priority
    --------
    1. QuakeML arrival takeoff angle.
    2. ObsPy TauP using the QuakeML earth_model_id for standard models.
    3. Embedded PB1D direct-ray solver when the origin model is PB1D.

    No silent straight-ray approximation is used.
    """
    qml = as_float(obs.qml_takeoff)
    if np.isfinite(qml) and 0.0 < qml <= 180.0:
        # QuakeML convention is opposite to HASH/SKHASH.
        return 180.0 - qml, "quakeml:flipped_to_HASH", np.nan, ""

    # Standard global model fallback, especially iasp91.
    angle, source, pred_tt, phase = estimate_takeoff_taup(
        origin, obs, station_row
    )
    if np.isfinite(angle):
        return angle, source, pred_tt, phase

    # Local PB1D fallback.
    model_id = _earth_model_name(origin).lower()
    if "pb1d" in model_id:
        angle, pred_tt = estimate_takeoff_pb1d(
            origin, station_row, distance_km
        )
        if np.isfinite(angle):
            return angle, "pb1d_direct_ray", pred_tt, "P"

    return np.nan, source or "unresolved", np.nan, ""



def build_s_pick_lookup(event, origin, use_zero_weight=False):
    """
    Build a station-keyed list of S picks belonging to the selected origin.
    """
    pick_map = {str(p.resource_id): p for p in event.picks}
    out = {}

    for arr in origin.arrivals:
        phase = (arr.phase or "").strip().upper()
        if not phase.startswith("S"):
            continue

        weight = as_float(arr.time_weight)
        if (not use_zero_weight) and np.isfinite(weight) and weight == 0.0:
            continue

        pick = pick_map.get(str(arr.pick_id))
        if pick is None or pick.waveform_id is None:
            continue

        wid = pick.waveform_id
        net = (wid.network_code or "").strip()
        sta = (wid.station_code or "").strip()
        loc = normalize_loc(wid.location_code)
        cha = (wid.channel_code or "").strip()
        if not sta:
            continue

        key = (net, sta)
        out.setdefault(key, []).append(
            {
                "time": pick.time,
                "location": loc,
                "channel": cha,
                "phase": phase,
                "weight": weight,
                "pick_id": str(pick.resource_id),
            }
        )

    for key in out:
        out[key].sort(key=lambda x: x["time"])
    return out


def choose_s_pick_for_p(obs, s_lookup):
    """
    Choose the first origin-associated S pick after the P pick at the same
    network/station. This is robust to S channel codes differing from P.
    """
    candidates = s_lookup.get((obs.network, obs.station), [])
    after = [s for s in candidates if s["time"] > obs.pick_time]
    if not after:
        return None
    return min(after, key=lambda x: x["time"] - obs.pick_time)


def _select_three_component_family(stream, obs, ptime, stime):
    """
    Select a co-located 3-C family for the historical st2sac_psamp method.

    The uploaded legacy code reads exactly three station components, then
    combines their variances. Here we identify Z + N/E (or Z + 1/2)
    explicitly instead of relying on Stream ordering.
    """
    groups = [
        stream.select(
            network=obs.network or "*",
            station=obs.station,
            location=obs.location if obs.location else "*",
        ),
        stream.select(
            network=obs.network or "*",
            station=obs.station,
        ),
        stream.select(station=obs.station),
    ]

    for group in groups:
        covering = [
            tr for tr in group
            if tr.stats.starttime <= ptime
            and tr.stats.endtime >= stime
        ]
        if not covering:
            continue

        by_prefix = {}
        for tr in covering:
            cha = str(tr.stats.channel)
            if len(cha) < 3:
                continue
            comp = cha[-1].upper()
            if comp not in {"Z", "N", "E", "1", "2"}:
                continue
            prefix = cha[:-1]
            by_prefix.setdefault(prefix, {})[comp] = tr

        candidates = []
        for prefix, d in by_prefix.items():
            if "Z" not in d:
                continue
            if "N" in d and "E" in d:
                h1, h2 = d["N"], d["E"]
            elif "1" in d and "2" in d:
                h1, h2 = d["1"], d["2"]
            else:
                continue

            z = d["Z"]
            srs = [
                float(z.stats.sampling_rate),
                float(h1.stats.sampling_rate),
                float(h2.stats.sampling_rate),
            ]
            # Legacy code implicitly assumes a common delta for all 3 comps.
            if max(srs) - min(srs) > 1e-6:
                continue

            candidates.append(
                (
                    min(srs),
                    prefix,
                    z,
                    h1,
                    h2,
                )
            )

        if candidates:
            candidates.sort(key=lambda x: (-x[0], x[1]))
            sr, prefix, z, h1, h2 = candidates[0]
            return {
                "prefix": prefix,
                "sampling_rate": sr,
                "z": z,
                "h1": h1,
                "h2": h2,
            }

    return None


def _legacy_psamp_preprocess_trace(tr):
    """
    Match st2sac_psamp(): demean + 5% taper, with NO bandpass/resampling.
    """
    x = tr.copy()
    try:
        x.detrend("demean")
    except Exception:
        x.data = np.asarray(x.data, dtype=float)
        x.data -= np.mean(x.data)

    try:
        x.taper(max_percentage=0.05)
    except Exception:
        pass

    data = np.asarray(x.data, dtype=float)
    if np.ma.isMaskedArray(data) and np.ma.getmaskarray(data).any():
        return None
    if not np.all(np.isfinite(data)):
        return None

    return x


def _slice_by_absolute_time(tr, t0, t1):
    """
    Slice by sample indices using the same round-to-sample logic as sac.py.
    The end index is exclusive, like Python slicing in the legacy routine.
    """
    sr = float(tr.stats.sampling_rate)
    i0 = int(round(float(t0 - tr.stats.starttime) * sr))
    i1 = int(round(float(t1 - tr.stats.starttime) * sr))

    if i0 < 0 or i1 > len(tr.data) or i1 <= i0:
        return None

    return np.asarray(tr.data[i0:i1], dtype=float)


def _sum_component_variances(segments):
    vals = []
    for x in segments:
        if x is None or len(x) < 2:
            return np.nan
        vals.append(float(np.var(np.asarray(x, dtype=float))))
    return float(np.sum(vals))


def measure_sp_ratio(
    stream,
    obs,
    s_pick,
    *,
    min_snr=1.0,
    wmax=9.0,
):
    """
    Closely reproduce the uploaded ``st2sac_psamp`` S/P calculation.

    Legacy method:
      1. require three components;
      2. demean + 5% taper each entire trace;
      3. require S-P >= 1 s;
      4. w = min(9 s, (S-P)/2);
      5. P window: [P - 0.05*w, P + w]
      6. S window: [S - 0.05*w, S + w]
      7. noise window has the SAME sample length as the P window and
         ends 2 s before P;
      8. combine variances from all three components;
      9. noise = sqrt(sum(var(noise_components)));
     10. P energy = sqrt(sum(var(P_components)) - noise_variance);
     11. S energy = sqrt(sum(var(S_components)) - noise_variance);
     12. PyHASH observed ratio = log10(S_energy / P_energy).

    The legacy helper also computed ``P_energy / S_energy`` for SAC user6,
    but HASH3 reads the written P and S amplitudes separately and SKHASH
    subsequently forms S/P. Therefore PyHASH must receive log10(S/P).
    """
    if s_pick is None:
        return None, "no_s_pick"

    ptime = obs.pick_time
    stime = s_pick["time"]
    ps = float(stime - ptime)

    if not np.isfinite(ps) or ps < 1.0:
        return None, "s_minus_p_below_1s"

    comps = _select_three_component_family(
        stream, obs, ptime, stime
    )
    if comps is None:
        return None, "three_component_waveforms_unavailable"

    w = min(float(wmax), ps / 2.0)
    if not np.isfinite(w) or w <= 0:
        return None, "invalid_sp_window"

    proc = []
    for tr in (comps["h1"], comps["h2"], comps["z"]):
        x = _legacy_psamp_preprocess_trace(tr)
        if x is None:
            return None, "sp_preprocessing_failed"
        proc.append(x)

    # Exact legacy time windows.
    p0 = ptime - 0.05 * w
    p1 = ptime + w
    s0 = stime - 0.05 * w
    s1 = stime + w

    # Legacy code defines a noise window of exactly the same number of
    # samples as the P window, ending 2 s before P.
    noise1 = ptime - 2.0
    noise0 = noise1 - (p1 - p0)

    pseg, sseg, nseg = [], [], []
    for tr in proc:
        pseg.append(_slice_by_absolute_time(tr, p0, p1))
        sseg.append(_slice_by_absolute_time(tr, s0, s1))
        nseg.append(_slice_by_absolute_time(tr, noise0, noise1))

    p_var = _sum_component_variances(pseg)
    s_var = _sum_component_variances(sseg)
    n_var = _sum_component_variances(nseg)

    if not all(np.isfinite(v) for v in (p_var, s_var, n_var)):
        return None, "sp_window_outside_trace_or_invalid"

    if n_var <= 0:
        return None, "nonpositive_sp_noise_variance"

    # This is the exact legacy SNR definition in sac.py.
    snr_legacy = np.sqrt(p_var) / np.sqrt(n_var)

    # HASH/SKHASH separately QC P and S amplitudes against their noise.
    p_signal_var = p_var - n_var
    s_signal_var = s_var - n_var

    if p_signal_var <= 0:
        return None, "p_energy_not_above_noise"
    if s_signal_var <= 0:
        return None, "s_energy_not_above_noise"

    p_energy = float(np.sqrt(p_signal_var))
    s_energy = float(np.sqrt(s_signal_var))
    noise = float(np.sqrt(n_var))

    p_snr = p_energy / noise
    s_snr = s_energy / noise

    if p_snr < float(min_snr):
        return None, f"p_snr_below_{min_snr:g}"
    if s_snr < float(min_snr):
        return None, f"s_snr_below_{min_snr:g}"

    sp_linear = s_energy / p_energy
    if not np.isfinite(sp_linear) or sp_linear <= 0:
        return None, "invalid_sp_ratio"

    # SKHASH converts amp_s/amp_p to log10 before grid search.
    sp_log10 = float(np.log10(round(sp_linear, 2)))
    if not np.isfinite(sp_log10):
        return None, "invalid_log10_sp_ratio"

    return {
        "sp_ratio": sp_log10,
        "sp_ratio_linear": float(sp_linear),
        "sp_amp_p": p_energy,
        "sp_amp_s": s_energy,
        "sp_noise_p": noise,
        "sp_noise_s": noise,
        "sp_snr_p": float(p_snr),
        "sp_snr_s": float(s_snr),
        "sp_snr_legacy": float(snr_legacy),
        "sp_channel_family": comps["prefix"],
        "sp_window_s": float(w),
        "sp_noise_window_start": str(noise0),
        "sp_noise_window_end": str(noise1),
        "s_pick_time": str(stime),
        "s_pick_phase": s_pick.get("phase", "S"),
        "p_to_s_time_s": float(ps),
    }, "ok"



def read_hash_reversal_file(path):
    """
    Read a traditional HASH/SKHASH station-polarity reversal file.

    Returns raw records; matching is intentionally permissive because legacy
    files vary in fixed-width details. Supported columns are station, channel,
    network, start, end when available.
    """
    if path is None:
        return []
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Polarity reversal file not found: {path}")

    records = []
    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        toks = line.split()
        if not toks:
            continue
        rec = {
            "station": toks[0].strip(),
            "channel": toks[1].strip() if len(toks) > 1 else "",
            "network": toks[2].strip() if len(toks) > 2 else "",
            "raw": raw,
        }
        records.append(rec)
    return records


def station_is_reversed(row, reversal_records):
    """
    Match station/channel/network against a legacy reversal list.

    A station match is required; network/channel are honored if supplied.
    """
    if not reversal_records:
        return False

    sta = str(row.get("station", "")).strip()
    net = str(row.get("network", "")).strip()
    cha = str(row.get("trace_id", "")).split(".")[-1].strip()

    for rec in reversal_records:
        if rec["station"] != sta:
            continue
        if rec["network"] and rec["network"] not in {net, "--"}:
            continue
        if rec["channel"] and rec["channel"] not in {cha, "--"}:
            continue
        return True
    return False


def read_sp_correction_file(path):
    """
    Read HASH-style station log10(S/P) corrections.

    Typical rows are:
        STATION CHANNEL NETWORK CORRECTION
    """
    corrections = {}
    if path is None:
        return corrections

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"S/P correction file not found: {path}")

    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        toks = line.split()
        if len(toks) < 4:
            continue
        sta, cha, net = toks[0], toks[1], toks[2]
        try:
            corr = float(toks[3])
        except Exception:
            continue
        corrections[(net, sta, cha)] = corr

    return corrections


def apply_sp_station_correction(row, corrections):
    """
    Apply a HASH station correction in log10-ratio space.
    """
    if not corrections or not np.isfinite(as_float(row.get("sp_ratio"))):
        return row

    net = str(row.get("network", "")).strip()
    sta = str(row.get("station", "")).strip()
    cha = str(row.get("sp_channel", "")).strip()

    keys = [
        (net, sta, cha),
        ("--", sta, cha),
    ]
    for key in keys:
        if key in corrections:
            corr = float(corrections[key])
            row["sp_station_correction"] = corr
            row["sp_ratio_uncorrected"] = float(row["sp_ratio"])
            # SKHASH applies station correction as:
            #     corrected_log10_SP = measured_log10_SP - sta_correction
            row["sp_ratio"] = float(row["sp_ratio"]) - corr
            return row

    return row



def prepare_observations(
    event,
    origin,
    stream,
    station_df,
    target_sr,
    confidence_threshold,
    use_zero_weight,
    use_manual_when_present,
    use_sp_ratio=True,
    sp_freqmin=1.0,
    sp_freqmax=20.0,
    sp_min_snr=1.0,
    legacy_eqp_preprocess=True,
    sp_corrections=None,
):
    """
    Prepare waveform windows and focal-sphere geometry independently.

    A missing QuakeML takeoff angle no longer discards an otherwise valid
    waveform. For iasp91/ak135/PREM origins, takeoff is reconstructed with
    ObsPy TauP. For PB1D origins, the embedded PB1D model is used as fallback.
    """
    pobs = extract_p_observations(
        event,
        origin,
        use_zero_weight=use_zero_weight,
    )
    s_lookup = build_s_pick_lookup(
        event,
        origin,
        use_zero_weight=use_zero_weight,
    )

    rows = []
    waveforms = []
    accepted_row_indices = []

    for obs in pobs:
        row = {
            "pick_id": obs.pick_id,
            "network": obs.network,
            "station": obs.station,
            "location": obs.location,
            "channel_requested": obs.channel,
            "pick_time": str(obs.pick_time),
            "qml_azimuth": obs.qml_azimuth,
            "qml_takeoff": obs.qml_takeoff,
            "qml_distance_deg": obs.qml_distance_deg,
            "qml_time_weight": obs.qml_time_weight,
            "manual_polarity": obs.manual_polarity,
            "accepted_for_eqpolarity": False,
            "geometry_ready": False,
            "accepted_for_pyhash": False,
            "reject_reason": "",
            "pyhash_reject_reason": "",
        }

        # ----------------------------------------------------------
        # A. Waveform matching/extraction first.
        # ----------------------------------------------------------
        tr, trace_match = choose_trace(stream, obs)
        row["trace_match"] = trace_match

        if tr is None:
            row["reject_reason"] = trace_match
            rows.append(row)
            continue

        row["trace_id"] = tr.id
        row["trace_sampling_rate_hz"] = float(tr.stats.sampling_rate)
        row["trace_starttime"] = str(tr.stats.starttime)
        row["trace_endtime"] = str(tr.stats.endtime)

        try:
            w = extract_centered_window(
                tr,
                obs.pick_time,
                target_sr=target_sr,
                n_samples=600,
                freqmin=1.0,
                freqmax=20.0,
                legacy_eqp_preprocess=legacy_eqp_preprocess,
            )
        except Exception as exc:
            row["reject_reason"] = f"waveform:{exc}"
            rows.append(row)
            continue

        row["accepted_for_eqpolarity"] = True

        # ----------------------------------------------------------
        # B. Station metadata and azimuth.
        # ----------------------------------------------------------
        station_row, station_match = station_row_for_pick(
            station_df,
            obs.network,
            obs.station,
            origin.time,
        )
        row["station_metadata_match"] = station_match

        distance_km = np.nan
        az = np.nan

        if station_row is not None:
            row["station_latitude"] = as_float(
                station_row["Latitude (WGS84)"]
            )
            row["station_longitude"] = as_float(
                station_row["Longitude (WGS84)"]
            )
            row["station_elevation_m"] = as_float(
                station_row["Elevation"]
            )

            try:
                distance_km, az_meta, baz = compute_geometry(
                    origin, station_row
                )
                az = float(az_meta)
                row["distance_km"] = distance_km
                row["azimuth"] = az
                row["back_azimuth"] = baz
                row["azimuth_vs_qml_deg"] = circular_difference_deg(
                    az, obs.qml_azimuth
                )
                row["azimuth_source"] = "station_metadata"
            except Exception as exc:
                row["station_geometry_warning"] = (
                    f"{type(exc).__name__}:{exc}"
                )

        # QuakeML arrival azimuth is an excellent fallback.
        if not np.isfinite(az) and np.isfinite(obs.qml_azimuth):
            az = float(obs.qml_azimuth) % 360.0
            row["azimuth"] = az
            row["azimuth_source"] = "quakeml_arrival"

        # If metadata distance failed, approximate from QuakeML degrees.
        if not np.isfinite(distance_km) and np.isfinite(obs.qml_distance_deg):
            distance_km = float(obs.qml_distance_deg) * 111.195
            row["distance_km"] = distance_km
            row["distance_source"] = "quakeml_degrees"
        elif np.isfinite(distance_km):
            row["distance_source"] = "station_metadata"

        # ----------------------------------------------------------
        # C. Takeoff angle.
        # ----------------------------------------------------------
        takeoff, takeoff_source, predicted_tt, taup_phase = (
            resolve_takeoff_angle(
                origin=origin,
                obs=obs,
                station_row=station_row,
                distance_km=distance_km,
            )
        )

        row["takeoff"] = takeoff
        row["takeoff_source"] = takeoff_source
        row["qml_takeoff_raw"] = obs.qml_takeoff
        row["predicted_p_travel_time_s"] = predicted_tt
        row["takeoff_phase"] = taup_phase
        row["observed_p_travel_time_s"] = as_float(
            obs.pick_time - origin.time
        )

        if (
            np.isfinite(predicted_tt)
            and np.isfinite(row["observed_p_travel_time_s"])
        ):
            row["p_travel_time_residual_s"] = (
                row["observed_p_travel_time_s"] - predicted_tt
            )

        # ----------------------------------------------------------
        # D. Optional S/P amplitude ratio.
        # ----------------------------------------------------------
        row["sp_ratio"] = np.nan
        row["sp_status"] = "disabled"

        if use_sp_ratio:
            s_pick = choose_s_pick_for_p(obs, s_lookup)
            sp_meas, sp_status = measure_sp_ratio(
                stream,
                obs,
                s_pick,
                min_snr=sp_min_snr,
                wmax=9.0,
            )
            row["sp_status"] = sp_status
            if sp_meas is not None:
                for k, v in sp_meas.items():
                    row[k] = v
                row = apply_sp_station_correction(
                    row, sp_corrections or {}
                )

        geometry_ready = (
            np.isfinite(az)
            and np.isfinite(takeoff)
            and 0.0 < float(takeoff) <= 180.0
        )
        row["geometry_ready"] = bool(geometry_ready)

        if not np.isfinite(az):
            row["pyhash_reject_reason"] = "azimuth_unresolved"
        elif not np.isfinite(takeoff):
            row["pyhash_reject_reason"] = "takeoff_unresolved"

        rows.append(row)
        waveforms.append(w)
        accepted_row_indices.append(len(rows) - 1)

    qc = pd.DataFrame(rows)

    if waveforms:
        waveforms = np.stack(waveforms).astype(np.float32)
    else:
        waveforms = np.empty((0, 600), dtype=np.float32)

    return qc, waveforms, accepted_row_indices


def print_qc_summary(qc):
    """Print waveform, geometry, and takeoff-source diagnostics."""
    print("\nQC summary")
    print("-" * 72)

    if qc.empty:
        print("No P-arrival rows were produced.")
        return

    eq_ok = qc["accepted_for_eqpolarity"].fillna(False).astype(bool)
    geo_ok = qc.get(
        "geometry_ready",
        pd.Series(False, index=qc.index),
    ).fillna(False).astype(bool)

    print(f"Total P arrivals considered : {len(qc)}")
    print(f"Usable EQPolarity windows   : {int(eq_ok.sum())}")
    print(f"Geometry ready for PyHASH   : {int((eq_ok & geo_ok).sum())}")
    print(f"Rejected before classifier  : {int((~eq_ok).sum())}")

    if (~eq_ok).any():
        print("\nWaveform rejection reasons:")
        reasons = (
            qc.loc[~eq_ok, "reject_reason"]
            .fillna("")
            .astype(str)
            .replace("", "unspecified")
            .value_counts()
        )
        for reason, count in reasons.items():
            print(f"  {count:3d}  {reason}")

    if "takeoff_source" in qc.columns:
        print("\nTakeoff-angle sources:")
        for src, count in (
            qc.loc[eq_ok, "takeoff_source"]
            .fillna("NA")
            .astype(str)
            .value_counts()
            .items()
        ):
            print(f"  {count:3d}  {src}")

    if "pyhash_reject_reason" in qc.columns:
        bad = (
            qc.loc[eq_ok & ~geo_ok, "pyhash_reject_reason"]
            .fillna("")
            .astype(str)
        )
        bad = bad[bad.str.len() > 0]
        if len(bad):
            print("\nGeometry rejection reasons:")
            for reason, count in bad.value_counts().items():
                print(f"  {count:3d}  {reason}")

    if "sp_status" in qc.columns:
        print("\nS/P amplitude-ratio QC:")
        for name, count in (
            qc.loc[eq_ok, "sp_status"]
            .fillna("NA")
            .astype(str)
            .value_counts()
            .items()
        ):
            print(f"  {count:3d}  {name}")
        if "sp_ratio" in qc.columns:
            nsp = int(np.isfinite(pd.to_numeric(qc["sp_ratio"], errors="coerce")).sum())
            print(f"  usable S/P ratios: {nsp}")

    if "trace_match" in qc.columns:
        print("\nTrace matching:")
        for name, count in (
            qc["trace_match"].fillna("NA").value_counts().items()
        ):
            print(f"  {count:3d}  {name}")

    if "station_metadata_match" in qc.columns:
        print("\nStation metadata matching:")
        for name, count in (
            qc["station_metadata_match"]
            .fillna("NA")
            .value_counts()
            .items()
        ):
            print(f"  {count:3d}  {name}")


def run_eqpolarity(
    qc,
    waveforms,
    accepted_row_indices,
    model_name,
    weights,
    device,
    confidence_threshold,
    use_manual_when_present,
    *,
    polarity_map="legacy",
    reversal_records=None,
):
    """
    Run EQPolarity and map its binary output to HASH polarity.

    polarity_map
    ------------
    legacy
        Reproduce the historical ``eqp.py`` behavior exactly:
        model class 1 -> HASH Up (+), class 0 -> HASH Down (-).
        This intentionally reverses the semantic comments in the old model
        code and is the mapping that fed the user's earlier HASH workflow.

    semantic
        Treat the model documentation literally:
        class 0 = Up (+), class 1 = Down (-).

    auto
        If >=3 manual QuakeML first motions exist, choose whichever mapping
        agrees with more of them. Otherwise fall back to ``legacy``.
    """
    from eqpolarity_torch import load_model, predict_proba

    model = load_model(
        model_name=model_name,
        weights=weights,
        device=device,
    )

    p1 = np.asarray(
        predict_proba(
            model,
            waveforms,
            batch_size=128,
            device=device,
        ),
        dtype=float,
    ).reshape(-1)

    # Determine mapping once per event.
    chosen = str(polarity_map).lower().strip()
    if chosen not in {"legacy", "semantic", "auto"}:
        raise ValueError(
            "--polarity-map must be legacy, semantic, or auto"
        )

    if chosen == "auto":
        labeled = []
        for ii, row_index in enumerate(accepted_row_indices):
            manual = manual_polarity_to_sign(
                qc.loc[row_index, "manual_polarity"]
            )
            if np.isfinite(manual):
                # legacy: p1>=.5 => +1
                sign_legacy = 1.0 if p1[ii] >= 0.5 else -1.0
                # semantic: p1>=.5 is Down => -1
                sign_semantic = -sign_legacy
                labeled.append(
                    (manual, sign_legacy, sign_semantic)
                )

        if len(labeled) >= 3:
            m = np.asarray([x[0] for x in labeled])
            leg = np.asarray([x[1] for x in labeled])
            sem = np.asarray([x[2] for x in labeled])
            aleg = float(np.mean(m == leg))
            asem = float(np.mean(m == sem))
            chosen = "legacy" if aleg >= asem else "semantic"
            print(
                "Auto polarity-map selection from QuakeML labels: "
                f"legacy agreement={aleg:.1%}, "
                f"semantic agreement={asem:.1%}; using {chosen}"
            )
        else:
            chosen = "legacy"
            print(
                "Auto polarity-map: fewer than 3 manual labels; "
                "using historical legacy mapping."
            )

    print(f"EQPolarity -> HASH mapping   : {chosen}")

    reversal_records = reversal_records or []

    for ii, row_index in enumerate(accepted_row_indices):
        prob1 = float(p1[ii])
        confidence = abs(2.0 * prob1 - 1.0)

        # Store raw network output without asserting class semantics.
        qc.loc[row_index, "eqpolarity_probability_class1"] = prob1

        # Backward-compatible name used by the waveform QC plot.
        # The trained EQPolarity model's sigmoid output is the original
        # class-1 probability (historically documented as Down).
        qc.loc[row_index, "p_down"] = prob1
        qc.loc[row_index, "polarity_confidence"] = confidence

        if chosen == "legacy":
            # Exact historical behavior in eqp.py:
            # output 1 -> U; output 0 -> D.
            hash_sign = 1.0 if prob1 >= 0.5 else -1.0
            model_label = "class1" if prob1 >= 0.5 else "class0"
        else:
            # Literal model documentation:
            # class0=Up, class1=Down.
            hash_sign = -1.0 if prob1 >= 0.5 else 1.0
            model_label = "Down" if prob1 >= 0.5 else "Up"

        qc.loc[row_index, "eqpolarity_binary_label"] = model_label
        qc.loc[row_index, "polarity_map_used"] = chosen
        qc.loc[row_index, "hash_polarity_before_reversal"] = hash_sign

        # Optional HASH station reversal table.
        if station_is_reversed(qc.loc[row_index], reversal_records):
            hash_sign *= -1.0
            qc.loc[row_index, "station_polarity_reversed"] = True
        else:
            qc.loc[row_index, "station_polarity_reversed"] = False

        # Preserve the DL confidence as a HASH weight.
        qc.loc[row_index, "pyhash_polarity_weight"] = (
            hash_sign * confidence
        )
        qc.loc[row_index, "predicted_hash_polarity"] = (
            "Up" if hash_sign > 0 else "Down"
        )

        manual_sign = manual_polarity_to_sign(
            qc.loc[row_index, "manual_polarity"]
        )
        qc.loc[row_index, "manual_polarity_sign"] = manual_sign
        if np.isfinite(manual_sign):
            qc.loc[row_index, "manual_model_agree"] = bool(
                manual_sign == hash_sign
            )

        geometry_ready = bool(qc.loc[row_index, "geometry_ready"])

        if use_manual_when_present and np.isfinite(manual_sign):
            qc.loc[row_index, "pyhash_polarity_weight"] = manual_sign
            qc.loc[row_index, "polarity_source"] = "manual_qml"
            polarity_ok = True
        elif confidence >= confidence_threshold:
            qc.loc[row_index, "polarity_source"] = (
                f"eqpolarity:{chosen}"
            )
            polarity_ok = True
        else:
            qc.loc[row_index, "polarity_source"] = (
                "eqpolarity_low_confidence"
            )
            polarity_ok = False
            qc.loc[row_index, "pyhash_reject_reason"] = (
                f"polarity_confidence_below_{confidence_threshold:g}"
            )

        qc.loc[row_index, "accepted_for_pyhash"] = bool(
            polarity_ok and geometry_ready
        )

        if polarity_ok and not geometry_ready:
            existing = str(
                qc.loc[row_index, "pyhash_reject_reason"] or ""
            ).strip()
            if not existing or existing.lower() == "nan":
                qc.loc[row_index, "pyhash_reject_reason"] = (
                    "focal_sphere_geometry_unresolved"
                )

    # Diagnostic comparison against manual labels.
    comp = qc[
        qc["manual_polarity_sign"].notna()
        & qc["pyhash_polarity_weight"].notna()
    ].copy()
    if len(comp) >= 3:
        model_sign = np.sign(
            comp["pyhash_polarity_weight"].to_numpy(float)
        )
        manual_sign = comp["manual_polarity_sign"].to_numpy(float)
        agreement = float(np.mean(model_sign == manual_sign))
        print(
            f"HASH-mapped EQPolarity vs QuakeML manual agreement: "
            f"{agreement:.1%} ({len(comp)} labeled stations)"
        )
        if agreement <= 0.25:
            warnings.warn(
                "The selected EQPolarity->HASH mapping strongly disagrees "
                "with available QuakeML manual polarities. Prefer "
                "--polarity-map auto unless you are intentionally "
                "reproducing a historical sign convention."
            )

    return qc




def compute_hash_coverage_gaps(azimuth_deg, takeoff_deg):
    """
    Reproduce SKHASH/HASH determine_max_gap exactly.

    Rays on the downgoing hemisphere are mirrored to the lower hemisphere
    before azimuth/takeoff gaps are computed.
    """
    az = np.asarray(azimuth_deg, dtype=float).copy()
    take = np.asarray(takeoff_deg, dtype=float).copy()

    good = np.isfinite(az) & np.isfinite(take)
    az = az[good]
    take = take[good]

    if len(az) < 2:
        return np.inf, np.inf

    flip = take > 90.0
    az[flip] -= 180.0
    take[flip] = 180.0 - take[flip]
    az[az < 0.0] += 360.0
    az %= 360.0

    az = np.sort(az)
    take = np.sort(take)

    az_gaps = np.diff(az)
    wrap_gap = az[0] + 360.0 - az[-1]
    agap = float(max(np.max(az_gaps), wrap_gap))

    take_gaps = np.diff(take)
    interior = float(np.max(take_gaps)) if len(take_gaps) else 0.0
    pgap = float(max(interior, take[0], 90.0 - take[-1]))

    return agap, pgap


def select_observations_with_adaptive_distance(
    use,
    *,
    max_distance_km=120.0,
    max_agap=90.0,
    max_pgap=60.0,
    policy="adaptive",
):
    """
    Apply the historical 120-km preference without sacrificing focal-sphere
    coverage unnecessarily.

    policy
    ------
    adaptive
        Start with <= max_distance_km. If HASH coverage fails, re-add the
        nearest excluded stations one by one until coverage passes or all
        observations have been restored.
    strict
        Enforce the distance cutoff even if focal-sphere coverage fails.
    none
        Use all accepted observations.
    """
    use = use.copy()

    if (
        policy == "none"
        or max_distance_km is None
        or max_distance_km <= 0
        or "distance_km" not in use.columns
    ):
        agap, pgap = compute_hash_coverage_gaps(
            use["azimuth"], use["takeoff"]
        )
        return use, agap, pgap, []

    dist = pd.to_numeric(use["distance_km"], errors="coerce")
    inside = dist.isna() | (dist <= float(max_distance_km))
    selected = use.loc[inside].copy()
    excluded = use.loc[~inside].copy()

    if len(selected) < 8 and policy == "adaptive":
        excluded = excluded.assign(
            _distance_sort=pd.to_numeric(
                excluded["distance_km"], errors="coerce"
            )
        ).sort_values("_distance_sort")

        added_rows = []
        for idx, row in excluded.iterrows():
            selected = pd.concat(
                [selected, use.loc[[idx]]],
                axis=0,
            )
            added_rows.append(idx)
            if len(selected) >= 8:
                break

        excluded = excluded.drop(index=added_rows, errors="ignore")

    agap, pgap = compute_hash_coverage_gaps(
        selected["azimuth"], selected["takeoff"]
    )

    restored = []

    if policy == "adaptive" and (
        agap > max_agap or pgap > max_pgap
    ):
        excluded = excluded.assign(
            _distance_sort=pd.to_numeric(
                excluded["distance_km"], errors="coerce"
            )
        ).sort_values("_distance_sort")

        for idx, row in excluded.iterrows():
            selected = pd.concat(
                [selected, use.loc[[idx]]],
                axis=0,
            )
            restored.append(
                (
                    str(row.get("station", "")),
                    float(row.get("_distance_sort", np.nan)),
                )
            )

            agap, pgap = compute_hash_coverage_gaps(
                selected["azimuth"], selected["takeoff"]
            )

            if agap <= max_agap and pgap <= max_pgap:
                break

    selected = selected.sort_index()
    return selected, agap, pgap, restored


def run_pyhash(
    qc,
    backend,
    max_agap,
    max_pgap,
    *,
    use_sp_ratio=True,
    nmc=30,
    azimuth_uncertainty_deg=1.0,
    takeoff_uncertainty_deg=5.0,
    max_distance_km=120.0,
    distance_policy="adaptive",
    strict_coverage=False,
):
    from pyhash import HashConfig, ObservationSet, solve

    use_all = qc[qc["accepted_for_pyhash"].fillna(False)].copy()

    required = ["azimuth", "takeoff", "pyhash_polarity_weight"]
    use_all = use_all.dropna(subset=required)

    if len(use_all) < 8:
        raise RuntimeError(
            f"Only {len(use_all)} polarities survived QC. "
            "PyHASH normally requires at least 8."
        )

    # ---------------------------------------------------------------
    # Historical HASH used 120 km, but do not let that artificial cutoff
    # destroy focal-sphere coverage. Adaptive mode restores the nearest
    # excluded stations until the requested coverage is reached.
    # ---------------------------------------------------------------
    use, agap, pgap, restored = select_observations_with_adaptive_distance(
        use_all,
        max_distance_km=max_distance_km,
        max_agap=max_agap,
        max_pgap=max_pgap,
        policy=distance_policy,
    )

    if distance_policy == "strict":
        removed = len(use_all) - len(use)
        if removed:
            print(
                f"Strict distance cutoff removed {removed} observations "
                f"beyond {max_distance_km:g} km."
            )
    elif distance_policy == "adaptive":
        initial_count = int(
            (
                pd.to_numeric(
                    use_all.get("distance_km", pd.Series(np.nan, index=use_all.index)),
                    errors="coerce",
                ).isna()
                | (
                    pd.to_numeric(
                        use_all.get("distance_km", pd.Series(np.nan, index=use_all.index)),
                        errors="coerce",
                    )
                    <= max_distance_km
                )
            ).sum()
        )
        print(
            f"Distance policy             : adaptive "
            f"(historical start <= {max_distance_km:g} km)"
        )
        print(
            f"Initial / final observations: "
            f"{initial_count} / {len(use)}"
        )
        if restored:
            restored_txt = ", ".join(
                f"{sta}({dist:.1f}km)"
                for sta, dist in restored
            )
            print(
                "Restored for coverage        : "
                + restored_txt
            )

    print(
        f"Nominal focal-sphere gaps   : "
        f"azimuth={agap:.1f}°, takeoff={pgap:.1f}°"
    )

    # If all usable stations still cannot satisfy the classic 90/60 test,
    # do not crash by default. Run the inversion, but preserve the actual
    # gap metrics so SKHASH quality grading will downgrade the mechanism.
    solver_max_agap = float(max_agap)
    solver_max_pgap = float(max_pgap)

    if agap > max_agap or pgap > max_pgap:
        msg = (
            "Focal-sphere coverage remains poorer than the requested "
            f"limits ({max_agap:g}°/{max_pgap:g}°): "
            f"{agap:.1f}°/{pgap:.1f}°."
        )

        if strict_coverage:
            raise ValueError(msg)

        warnings.warn(
            msg
            + " Continuing with all available information; the returned "
              "mechanism will retain its true coverage gaps and should be "
              "treated as lower confidence."
        )
        solver_max_agap = max(solver_max_agap, agap + 0.01)
        solver_max_pgap = max(solver_max_pgap, pgap + 0.01)

    az0 = use["azimuth"].to_numpy(float)
    to0 = use["takeoff"].to_numpy(float)
    pol = use["pyhash_polarity_weight"].to_numpy(float)

    if use_sp_ratio and "sp_ratio" in use.columns:
        sp = pd.to_numeric(
            use["sp_ratio"], errors="coerce"
        ).to_numpy(float)
    else:
        sp = np.full(len(use), np.nan, dtype=float)

    nmc = max(1, int(nmc))
    rng = np.random.default_rng(123)

    az = np.repeat(az0[:, None], nmc, axis=1)
    takeoff = np.repeat(to0[:, None], nmc, axis=1)

    if nmc > 1:
        az[:, 1:] += rng.normal(
            0.0,
            float(azimuth_uncertainty_deg),
            size=(len(use), nmc - 1),
        )
        takeoff[:, 1:] += rng.normal(
            0.0,
            float(takeoff_uncertainty_deg),
            size=(len(use), nmc - 1),
        )

    az %= 360.0
    takeoff = np.where(takeoff < 0.0, -takeoff, takeoff)
    takeoff = np.where(
        takeoff > 180.0, 360.0 - takeoff, takeoff
    )
    takeoff = np.clip(takeoff, 0.01, 179.99)

    obs = ObservationSet(
        azimuth=az,
        takeoff=takeoff,
        polarity=pol,
        sp_ratio=sp,
        station=use["station"].astype(str).to_numpy(),
    )

    cfg = HashConfig(
        dang=5.0,
        nmc=nmc,
        maxout=300,
        badfrac=0.10,
        badmin=2.0,
        qbadfrac=0.30,
        qbadmin=2.0,
        cangle=45.0,
        prob_max=0.25,
        max_agap=solver_max_agap,
        max_pgap=solver_max_pgap,
        backend=backend,
        seed=123,
        deterministic=True,
    )

    mech, raw, pol_agree, sp_diff = solve(obs, cfg)

    use["mechanism_polarity_agrees"] = np.asarray(
        pol_agree, dtype=bool
    )
    use["sp_difference_log10"] = np.asarray(
        sp_diff, dtype=float
    )

    # Add provenance so outputs document exactly how coverage was handled.
    use["coverage_azimuth_gap_deg"] = agap
    use["coverage_takeoff_gap_deg"] = pgap
    use["distance_policy"] = distance_policy
    use["nominal_max_distance_km"] = max_distance_km

    return mech, raw, use, cfg



def plot_waveform_qc(qc, waveforms, accepted_row_indices, outpath, show, sampling_rate=100.0):
    import matplotlib.pyplot as plt

    n = len(waveforms)
    if n == 0:
        return

    # Sort only for visualization.
    view = []
    for ii, ri in enumerate(accepted_row_indices):
        row = qc.loc[ri]
        view.append(
            (
                as_float(row.get("azimuth")),
                str(row.get("station")),
                ii,
                ri,
            )
        )
    view.sort(key=lambda x: (x[0], x[1]))

    ncols = 4
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(13, max(3.0, 2.2 * nrows)),
        squeeze=False,
    )
    axes = axes.ravel()

    # Legacy eqp.py places P at sample 299; modern preprocessing uses 300.
    p_plot_index = 299
    t = (np.arange(600) - p_plot_index) / float(sampling_rate)

    for ax, (_, _, wi, ri) in zip(axes, view):
        row = qc.loc[ri]
        w = waveforms[wi]
        ax.plot(t, w, lw=0.8)
        ax.axvline(0.0, lw=0.8, ls="--")
        ax.set_xlim(t[0], t[-1])
        ax.set_ylim(-1.08, 1.08)

        pdn = as_float(
            row.get(
                "p_down",
                row.get("eqpolarity_probability_class1", np.nan),
            )
        )
        conf = as_float(row.get("polarity_confidence"))
        hash_pol = str(row.get("predicted_hash_polarity", "?"))
        accepted = bool(row.get("accepted_for_pyhash", False))

        # P(D) is the raw Texas EQPolarity sigmoid output. HASH polarity may
        # be remapped/reversed separately; display both to avoid ambiguity.
        ax.set_title(
            f"{row['network']}.{row['station']}  "
            f"HASH={hash_pol}\n"
            f"P(D)={pdn:.2f}  conf={conf:.2f}  use={accepted}",
            fontsize=8,
        )
        ax.tick_params(labelsize=7)

    for ax in axes[n:]:
        ax.axis("off")

    fig.suptitle(
        "EQPolarity input windows: P arrival at t = 0 s",
        fontsize=13,
    )
    fig.supxlabel("Time relative to P arrival (s)")
    fig.supylabel("Normalized amplitude")
    fig.tight_layout()
    fig.savefig(outpath, dpi=200, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_mechanism(mech, used, origin, outpath, show):
    import matplotlib.pyplot as plt
    from pyhash.plotting import beach, takeoff_az2xy

    if mech.empty:
        raise RuntimeError("PyHASH returned an empty mechanism table.")

    best = mech.iloc[0]
    strike = float(best["str_avg"])
    dip = float(best["dip_avg"])
    rake = float(best["rak_avg"])

    fig = plt.figure(figsize=(11, 5))

    # Panel 1: beachball.
    ax1 = fig.add_subplot(1, 2, 1)
    # pyhash.plotting.beach is the SKHASH-compatible helper, not
    # obspy.imaging.beachball.beach.  It returns a PatchCollection already
    # centered on the unit focal sphere and therefore does not accept
    # ObsPy's ``xy`` or ``width`` keywords.
    bb = beach(
        strike,
        dip,
        rake,
        facecolor="k",
        bgcolor="w",
        edgecolor="k",
        linewidth=1.0,
        zorder=2,
    )
    ax1.add_collection(bb)
    ax1.set_xlim(-1.05, 1.05)
    ax1.set_ylim(-1.05, 1.05)
    ax1.set_aspect("equal")
    ax1.axis("off")
    qual = str(best.get("qual", ""))
    prob = as_float(best.get("prob"))

    ax1.set_title(
        f"PyHASH preferred mechanism\n"
        f"Strike/Dip/Rake = {strike:.1f}/{dip:.1f}/{rake:.1f}°\n"
        f"Quality={qual}   probability={prob:.3f}"
    )

    # Panel 2: focal-sphere station distribution.
    ax2 = fig.add_subplot(1, 2, 2)
    theta = np.linspace(0, 2 * np.pi, 361)
    ax2.plot(np.cos(theta), np.sin(theta), lw=1.0)

    for _, r in used.iterrows():
        try:
            xy = takeoff_az2xy(
                np.asarray([float(r["takeoff"])]),
                np.asarray([float(r["azimuth"])]),
            )
            xy = np.asarray(xy, dtype=float).reshape(-1, 2)
            x = float(xy[0, 0])
            y = float(xy[0, 1])
        except Exception:
            # Equal-area lower-hemisphere fallback.
            take = float(r["takeoff"])
            az = math.radians(float(r["azimuth"]))
            if take > 90:
                take = 180 - take
                az += math.pi
            radius = math.sqrt(2.0) * math.sin(
                math.radians(take) / 2.0
            )
            x = radius * math.sin(az)
            y = radius * math.cos(az)

        weight = float(r["pyhash_polarity_weight"])
        marker = "^" if weight > 0 else "v"
        filled = bool(r.get("mechanism_polarity_agrees", True))

        ax2.scatter(
            [x],
            [y],
            marker=marker,
            s=45,
            facecolors="k" if filled else "none",
            edgecolors="k",
            linewidths=0.8,
        )
        ax2.text(
            x + 0.025,
            y + 0.025,
            str(r["station"]),
            fontsize=6,
        )

    ax2.set_aspect("equal")
    ax2.set_xlim(-1.12, 1.12)
    ax2.set_ylim(-1.12, 1.12)
    ax2.axis("off")
    ax2.set_title(
        "Focal-sphere coverage\n"
        "▲ Up   ▼ Down; open = polarity misfit"
    )

    fig.suptitle(
        f"TexNet event {origin.time}   "
        f"lat={origin.latitude:.4f}, lon={origin.longitude:.4f}, "
        f"depth={origin.depth/1000.0:.2f} km",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(outpath, dpi=220, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)


def write_velocity_model(outdir):
    p = outdir / "PB1D_velocity_model.txt"
    p.write_text(
        "# depth_km Vp_km_s Vs_km_s density Qp Qs\n"
        + PB1Dvel
        + "\n"
    )
    return p


def summarize(event, origin, mag, qc, mech, raw, used, outdir, cfg):
    best = mech.iloc[0]
    summary = {
        "event_resource_id": str(event.resource_id),
        "origin_time": str(origin.time),
        "latitude": float(origin.latitude),
        "longitude": float(origin.longitude),
        "depth_km": float(origin.depth) / 1000.0
        if origin.depth is not None
        else None,
        "earth_model_id": str(origin.earth_model_id)
        if origin.earth_model_id
        else None,
        "magnitude": float(mag.mag) if mag and mag.mag is not None else None,
        "magnitude_type": str(mag.magnitude_type) if mag else None,
        "n_p_arrivals_considered": int(len(qc)),
        "n_waveforms_classified": int(
            qc["accepted_for_eqpolarity"].fillna(False).sum()
        ),
        "n_polarities_used_by_pyhash": int(len(used)),
        "n_sp_ratios_used_by_pyhash": int(
            np.isfinite(pd.to_numeric(
                used.get("sp_ratio", pd.Series(dtype=float)),
                errors="coerce",
            )).sum()
        ),
        "pyhash_backend": cfg.backend,
        "pyhash_n_accepted_grid_solutions": int(raw.n_accepted),
        "strike_deg": float(best["str_avg"]),
        "dip_deg": float(best["dip_avg"]),
        "rake_deg": float(best["rak_avg"]),
        "probability": as_float(best.get("prob")),
        "quality": str(best.get("qual", "")),
        "polarity_misfit_fraction": as_float(best.get("mfrac")),
        "station_distribution_ratio": as_float(best.get("stdr")),
        "azimuthal_gap_deg": as_float(best.get("azimuthal_gap")),
        "takeoff_gap_deg": as_float(best.get("takeoff_gap")),
    }

    (outdir / "summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    return summary


def parse_args():
    p = argparse.ArgumentParser(
        description=(
            "TexNet QuakeML + miniSEED -> EQPolarity-Torch -> PyHASH "
            "focal mechanism"
        )
    )
    p.add_argument("--qml", type=Path, default=DEFAULT_QML)
    p.add_argument("--mseed", type=Path, default=DEFAULT_MSEED)
    p.add_argument("--stations", type=Path, default=DEFAULT_STATIONS)
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("%s_focal_mechanism"%eid),
    )
    p.add_argument(
        "--model",
        default="texas",
        choices=["texas", "scsn"],
        help="EQPolarity model; Texas transfer model is recommended here.",
    )
    p.add_argument(
        "--weights",
        type=Path,
        default=None,
        help="Optional explicit .pt or original .h5 EQPolarity weights.",
    )
    p.add_argument(
        "--device",
        default=None,
        help="Torch device, e.g. cpu, cuda, mps. Default: auto.",
    )
    p.add_argument(
        "--sampling-rate",
        type=float,
        default=100.0,
        help="Target EQPolarity sampling rate. Default 100 Hz.",
    )
    p.add_argument(
        "--min-confidence",
        type=float,
        default=0.15,
        help=(
            "Minimum abs(2*P(Down)-1) for using an EQPolarity pick in "
            "PyHASH. Default 0.15."
        ),
    )
    p.add_argument(
        "--backend",
        default="numpy",
        choices=["numpy", "torch"],
        help="PyHASH search backend. NumPy is the safest reference backend.",
    )
    p.add_argument(
        "--polarity-map",
        choices=["legacy", "semantic", "auto"],
        default="auto",
        help=(
            "Map EQPolarity binary output to HASH sign. 'legacy' exactly "
            "reproduces eqp.py (class1->Up, class0->Down); 'semantic' uses "
            "the documented 0=Up,1=Down meaning; 'auto' uses manual labels "
            "when available. Default: legacy."
        ),
    )
    p.add_argument(
        "--polarity-reversal-file",
        type=Path,
        default=None,
        help=(
            "Optional traditional HASH station polarity-reversal file. "
            "Matched station/channel/network polarities are sign-flipped."
        ),
    )
    p.add_argument(
        "--sp-correction-file",
        type=Path,
        default=None,
        help=(
            "Optional HASH station S/P log10 correction file "
            "(station channel network correction)."
        ),
    )
    p.add_argument(
        "--modern-eqp-preprocess",
        action="store_true",
        help=(
            "Use the newer centered/no-legacy preprocessing instead of the "
            "historical eqp.py 1-20 Hz, P-index-299 preprocessing."
        ),
    )
    p.add_argument(
        "--no-sp-ratio",
        action="store_true",
        help=(
            "Disable three-component S/P amplitude-ratio constraints. "
            "By default S/P is ENABLED for this workflow."
        ),
    )
    p.add_argument(
        "--sp-freqmin",
        type=float,
        default=1.0,
        help=(
            "Retained for CLI compatibility. The default legacy "
            "st2sac_psamp-compatible S/P calculation does NOT bandpass."
        ),
    )
    p.add_argument(
        "--sp-freqmax",
        type=float,
        default=20.0,
        help=(
            "Retained for CLI compatibility. The default legacy "
            "st2sac_psamp-compatible S/P calculation does NOT bandpass."
        ),
    )
    p.add_argument(
        "--sp-min-snr",
        type=float,
        default=1.0,
        help=(
            "Minimum independent P and S amplitude SNR for using S/P. "
            "Default 1.0 matches the historical HASH-driver3 workflow."
        ),
    )
    p.add_argument(
        "--nmc",
        type=int,
        default=30,
        help=(
            "Number of geometry Monte Carlo trials. Default 30 matches the "
            "historical HASH-driver3 workflow."
        ),
    )
    p.add_argument(
        "--azimuth-uncertainty",
        type=float,
        default=1.0,
        help="1-sigma azimuth perturbation for Monte Carlo trials (degrees).",
    )
    p.add_argument(
        "--takeoff-uncertainty",
        type=float,
        default=5.0,
        help="1-sigma takeoff perturbation for Monte Carlo trials (degrees).",
    )
    p.add_argument(
        "--max-azimuth-gap",
        type=float,
        default=90.0,
        help="Maximum allowed PyHASH azimuthal gap.",
    )
    p.add_argument(
        "--max-distance-km",
        type=float,
        default=120.0,
        help=(
            "Historical preferred source-station distance limit. "
            "Default 120 km."
        ),
    )
    p.add_argument(
        "--distance-policy",
        choices=["adaptive", "strict", "none"],
        default="adaptive",
        help=(
            "How to apply --max-distance-km. 'adaptive' starts at the "
            "historical cutoff and restores nearest farther stations until "
            "focal-sphere coverage improves; 'strict' enforces the cutoff; "
            "'none' uses every accepted station. Default: adaptive."
        ),
    )
    p.add_argument(
        "--strict-coverage",
        action="store_true",
        help=(
            "Abort when azimuth/takeoff gaps exceed requested limits. "
            "Default is to continue with a warning and let the SKHASH "
            "quality grade reflect poor coverage."
        ),
    )
    p.add_argument(
        "--max-takeoff-gap",
        type=float,
        default=60.0,
        help="Maximum allowed PyHASH takeoff-angle gap.",
    )
    p.add_argument(
        "--use-zero-weight-arrivals",
        action="store_true",
        help=(
            "Also consider preferred-origin arrivals whose QuakeML "
            "time_weight is zero."
        ),
    )
    p.add_argument(
        "--use-manual-when-present",
        action="store_true",
        help=(
            "If QuakeML already has a manual positive/negative polarity, "
            "use it instead of the model prediction for PyHASH. "
            "Default: model prediction only."
        ),
    )
    p.add_argument(
        "--show",
        action="store_true",
        help="Display figures interactively in addition to saving PNGs.",
    )
    return p.parse_args()


def main():
    args = parse_args()
    require_runtime()

    from obspy import read, read_events

    for path, label in [
        (args.qml, "QuakeML"),
        (args.mseed, "miniSEED"),
        (args.stations, "station CSV"),
    ]:
        if not path.exists():
            raise FileNotFoundError(f"{label} file does not exist: {path}")

    if not (0.0 <= args.min_confidence <= 1.0):
        raise ValueError("--min-confidence must be between 0 and 1.")
    if args.sampling_rate <= 0:
        raise ValueError("--sampling-rate must be positive.")

    outdir = args.output_dir.expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("TexNet EQPolarity-Torch -> PyHASH focal-mechanism workflow")
    print("=" * 72)

    print(f"Reading QuakeML : {args.qml}")
    cat = read_events(str(args.qml))
    if len(cat) == 0:
        raise RuntimeError("No events found in QuakeML.")
    if len(cat) > 1:
        warnings.warn(
            f"QuakeML contains {len(cat)} events; using the first event."
        )

    event = cat[0]
    origin = get_preferred_origin(event)
    mag = get_preferred_magnitude(event)

    earth_model_name = _earth_model_name(origin)
    if "pb1d" in earth_model_name.lower():
        write_velocity_model(outdir)

    print(
        f"Event            : {event.resource_id}\n"
        f"Origin time      : {origin.time}\n"
        f"Latitude         : {origin.latitude:.6f}\n"
        f"Longitude        : {origin.longitude:.6f}\n"
        f"Depth            : {origin.depth/1000.0:.3f} km"
    )
    if origin.earth_model_id:
        print(f"Origin earth model: {origin.earth_model_id}")
    if mag:
        print(f"Magnitude         : {mag.mag} {mag.magnitude_type}")

    print(f"Reading miniSEED : {args.mseed}")
    stream = read(str(args.mseed))
    if len(stream) == 0:
        raise RuntimeError("miniSEED contains no traces.")

    # Do not globally merge traces: merging can silently interpolate gaps.
    print(
        f"Waveform traces  : {len(stream)} "
        f"({len(set(tr.id for tr in stream))} unique IDs)"
    )

    print(f"Reading stations : {args.stations}")
    station_df = load_station_metadata(args.stations)

    reversal_records = read_hash_reversal_file(
        args.polarity_reversal_file
    )
    sp_corrections = read_sp_correction_file(
        args.sp_correction_file
    )
    if reversal_records:
        print(
            f"Loaded polarity reversals : {len(reversal_records)} records"
        )
    if sp_corrections:
        print(
            f"Loaded S/P corrections    : {len(sp_corrections)} records"
        )

    qc, waveforms, accepted_row_indices = prepare_observations(
        event=event,
        origin=origin,
        stream=stream,
        station_df=station_df,
        target_sr=args.sampling_rate,
        confidence_threshold=args.min_confidence,
        use_zero_weight=args.use_zero_weight_arrivals,
        use_manual_when_present=args.use_manual_when_present,
        use_sp_ratio=not args.no_sp_ratio,
        sp_freqmin=args.sp_freqmin,
        sp_freqmax=args.sp_freqmax,
        sp_min_snr=args.sp_min_snr,
        legacy_eqp_preprocess=not args.modern_eqp_preprocess,
        sp_corrections=sp_corrections,
    )

    print(
        f"P arrivals after origin-QC : {len(qc)}\n"
        f"Usable waveform windows    : "
        f"{qc['accepted_for_eqpolarity'].fillna(False).sum()}"
    )

    print_qc_summary(qc)
    qc.to_csv(outdir / "polarity_qc_preclassifier.csv", index=False)

    if len(waveforms) == 0:
        raise RuntimeError(
            "No usable P-wave windows survived waveform QC. "
            f"Inspect {outdir / 'polarity_qc_preclassifier.csv'}."
        )

    qc = run_eqpolarity(
        qc=qc,
        waveforms=waveforms,
        accepted_row_indices=accepted_row_indices,
        model_name=args.model,
        weights=args.weights,
        device=args.device,
        confidence_threshold=args.min_confidence,
        use_manual_when_present=args.use_manual_when_present,
        polarity_map=args.polarity_map,
        reversal_records=reversal_records,
    )

    nuse = int(qc["accepted_for_pyhash"].fillna(False).sum())
    print(f"Polarities retained for PyHASH: {nuse}")
    if "sp_ratio" in qc.columns:
        nsp = int(np.isfinite(pd.to_numeric(qc["sp_ratio"], errors="coerce")).sum())
        print(f"S/P ratios retained           : {nsp}")
    print(
        "Takeoff convention           : HASH/SKHASH "
        "(<90 upgoing, >90 downgoing)"
    )
    print(
        "EQPolarity preprocessing     : "
        + (
            "legacy eqp.py (linear detrend, 1-20 Hz, P index 299)"
            if not args.modern_eqp_preprocess
            else "modern centered preprocessing"
        )
    )
    print(
        "S/P measurement              : "
        + (
            "legacy st2sac_psamp variance-energy method"
            if not args.no_sp_ratio
            else "disabled"
        )
    )
    print(f"Distance policy              : {args.distance_policy}")
    print(
        "Coverage handling            : "
        + ("strict" if args.strict_coverage else "warn-and-continue")
    )

    # Save classifier inputs for reproducibility.
    np.save(outdir / "eqpolarity_600sample_windows.npy", waveforms)
    qc.to_csv(outdir / "polarity_qc_all.csv", index=False)

    plot_waveform_qc(
        qc,
        waveforms,
        accepted_row_indices,
        outdir / "eqpolarity_waveform_qc.png",
        show=args.show,
        sampling_rate=args.sampling_rate,
    )

    mech, raw, used, cfg = run_pyhash(
        qc=qc,
        backend=args.backend,
        max_agap=args.max_azimuth_gap,
        max_pgap=args.max_takeoff_gap,
        use_sp_ratio=not args.no_sp_ratio,
        nmc=args.nmc,
        azimuth_uncertainty_deg=args.azimuth_uncertainty,
        takeoff_uncertainty_deg=args.takeoff_uncertainty,
        max_distance_km=args.max_distance_km,
        distance_policy=args.distance_policy,
        strict_coverage=args.strict_coverage,
    )

    mech.to_csv(outdir / "pyhash_mechanisms.csv", index=False)
    used.to_csv(outdir / "pyhash_used_polarities.csv", index=False)

    plot_mechanism(
        mech,
        used,
        origin,
        outdir / "pyhash_focal_mechanism.png",
        show=args.show,
    )

    summary = summarize(
        event,
        origin,
        mag,
        qc,
        mech,
        raw,
        used,
        outdir,
        cfg,
    )

    best = mech.iloc[0]
    print("\n" + "=" * 72)
    print("RESULT")
    print("=" * 72)
    print(
        f"Strike / Dip / Rake : "
        f"{best['str_avg']:.1f} / "
        f"{best['dip_avg']:.1f} / "
        f"{best['rak_avg']:.1f} deg"
    )
    print(f"Quality             : {best.get('qual', '')}")
    print(f"Probability         : {best.get('prob', np.nan):.3f}")
    print(
        f"Polarity misfit     : "
        f"{best.get('mfrac', np.nan):.3f}"
    )
    print(
        f"Azimuthal gap       : "
        f"{best.get('azimuthal_gap', np.nan):.1f} deg"
    )
    print(
        f"Takeoff gap         : "
        f"{best.get('takeoff_gap', np.nan):.1f} deg"
    )
    print(f"Accepted grid mechs : {raw.n_accepted}")
    print(f"Output directory    : {outdir}")

    print("\nFiles written:")
    names = [
        "polarity_qc_preclassifier.csv",
        "eqpolarity_600sample_windows.npy",
        "polarity_qc_all.csv",
        "eqpolarity_waveform_qc.png",
        "pyhash_used_polarities.csv",
        "pyhash_mechanisms.csv",
        "pyhash_focal_mechanism.png",
        "summary.json",
    ]
    if "pb1d" in earth_model_name.lower():
        names.insert(0, "PB1D_velocity_model.txt")
    for name in names:
        print(f"  {outdir / name}")


if __name__ == "__main__":
    main()
