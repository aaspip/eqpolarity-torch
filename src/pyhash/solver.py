from __future__ import annotations
import numpy as np
from .config import HashConfig
from .types import ObservationSet
from .grid import search
from .legacy import fun as _f

DEFAULT_QUALITY={
 'qual_letter':np.asarray(['A','B','C','D']),
 'probs':np.asarray([0.8,0.6,0.5,0.0]),
 'var_avg':np.asarray([25.,35.,45.,np.inf]),
 'mfrac':np.asarray([0.15,0.20,0.30,np.inf]),
 'stdr':np.asarray([0.5,0.4,0.3,0.0]),
 'azimuthal_gap':90.,'takeoff_gap':60.,'num_p_pol':8,
}

def solve(obs: ObservationSet, cfg: HashConfig=HashConfig(), quality_criteria=None):
    """Solve one event from precomputed azimuth/takeoff observations.

    Returns a pandas DataFrame with preferred mechanism(s) and the raw accepted
    grid result. This small API is convenient for EQPolarity -> PyHASH use.
    """
    cfg=cfg.validated()
    agap,pgap=_f.determine_max_gap(obs.azimuth[:,0].copy(),obs.takeoff[:,0].copy())
    if agap>cfg.max_agap or pgap>cfg.max_pgap:
        raise ValueError(f'insufficient focal-sphere coverage: azimuth gap={agap:.1f}, takeoff gap={pgap:.1f}')
    raw=search(obs,cfg)
    if raw.n_accepted==0:
        raise RuntimeError('no acceptable focal mechanism solutions')
    mech=_f.mech_probability(raw.fault_normals,raw.fault_slips,cfg.cangle,cfg.prob_max,iterative_avg=False)
    mech,pol_agree,sp_diff=_f.mech_misfit(mech,obs.azimuth[:,0],obs.takeoff[:,0],obs.polarity,obs.sp_ratio)
    mech['num_p_pol']=int(np.sum(obs.polarity!=0)); mech['num_sp_ratios']=int(np.isfinite(obs.sp_ratio).sum())
    mech['azimuthal_gap']=agap; mech['takeoff_gap']=pgap
    mech=_f.mech_quality(mech, quality_criteria or DEFAULT_QUALITY)
    return mech,raw,pol_agree,sp_diff
