from __future__ import annotations
from functools import lru_cache
import numpy as np
from .config import HashConfig
from .types import ObservationSet, GridSearchResult
from .legacy import fun as legacy_fun

@lru_cache(maxsize=16)
def direction_grid(dang: float=5.0, include_amplitudes: bool=True, min_amp: float=5e-4):
    """Create and cache the HASH direction-cosine grid.

    This is mathematically identical to SKHASH ``dir_cos_setup`` but avoids
    rebuilding the expensive grid for every run/process in a Python session.
    """
    return legacy_fun.dir_cos_setup({'dang':float(dang),'ampfile':bool(include_amplitudes),'min_amp':float(min_amp)})

def _thresholds(pol: np.ndarray, sp: np.ndarray, cfg: HashConfig):
    sw=float(np.abs(pol[np.isfinite(pol)]).sum())
    nextra=max(round(sw*cfg.badfrac*0.5),cfg.badmin)
    ntotal=max(round(sw*cfg.badfrac),cfg.badmin)
    nspr=int(np.isfinite(sp).sum())
    qextra=max(nspr*cfg.qbadfrac*0.5,cfg.qbadmin) if nspr else 0.0
    qtotal=max(nspr*cfg.qbadfrac,cfg.qbadmin) if nspr else 0.0
    return nextra,ntotal,qextra,qtotal

def search_numpy(obs: ObservationSet, cfg: HashConfig=HashConfig()) -> GridSearchResult:
    """Faithful NumPy backend using the validated SKHASH mathematics.

    The grid is cached and inputs are contiguous. The acceptance equations are
    delegated to the reference implementation so this backend is the safest
    choice when reproducing published SKHASH examples.
    """
    cfg=cfg.validated()
    grid=direction_grid(cfg.dang, bool(np.isfinite(obs.sp_ratio).any()), cfg.min_amp)
    nextra,ntotal,qextra,qtotal=_thresholds(obs.polarity,obs.sp_ratio,cfg)
    # Legacy function has deterministic RNG seed 123 and exact acceptance logic.
    n,s=legacy_fun.focal_gridsearch(np.ascontiguousarray(obs.azimuth),np.ascontiguousarray(obs.takeoff),
        np.ascontiguousarray(obs.polarity),np.ascontiguousarray(obs.sp_ratio),grid,
        nextra,ntotal,qextra,qtotal,cfg.maxout,grid['ncoor'])
    # Recover grid indices when possible (used only for diagnostics).
    idx=np.empty(n.shape[1],dtype=int)
    if n.shape[1]:
        dots=grid['b3'].T@n
        idx=np.argmax(dots,axis=0)
    return GridSearchResult(n,s,idx,'numpy',int(grid['ncoor']),int(n.shape[1]))

def search_torch(obs: ObservationSet, cfg: HashConfig=HashConfig(backend='torch')) -> GridSearchResult:
    """Torch-accelerated polarity grid search (CPU, CUDA or MPS).

    The acceptance criterion matches SKHASH for polarity-only inversions.
    S/P-constrained inversions currently fall back to the exact NumPy backend,
    because preserving the table-indexing edge behavior is more important than
    silently changing published solutions.
    """
    import torch
    cfg=cfg.validated()
    if np.isfinite(obs.sp_ratio).any():
        return search_numpy(obs,cfg.with_updates(backend='numpy'))
    if cfg.device=='auto':
        device='cuda' if torch.cuda.is_available() else ('mps' if getattr(torch.backends,'mps',None) and torch.backends.mps.is_available() else 'cpu')
    else: device=cfg.device
    dtype=torch.float32 if cfg.dtype=='float32' else torch.float64
    grid=direction_grid(cfg.dang,False,cfg.min_amp)
    b1=torch.as_tensor(grid['b1'],dtype=dtype,device=device)
    b3=torch.as_tensor(grid['b3'],dtype=dtype,device=device)
    pol=np.asarray(obs.polarity,float)
    use=np.flatnonzero(np.isfinite(pol)&(pol!=0))
    az=torch.as_tensor(np.deg2rad(obs.azimuth[use]),dtype=dtype,device=device)
    to=torch.as_tensor(np.deg2rad(obs.takeoff[use]),dtype=dtype,device=device)
    p=torch.as_tensor(pol[use],dtype=dtype,device=device)
    xyz=torch.stack((torch.sin(to)*torch.cos(az),torch.sin(to)*torch.sin(az),-torch.cos(to)),dim=0)
    nextra,ntotal,_,_=_thresholds(pol,np.full(len(pol),np.nan),cfg)
    accepted=torch.zeros(grid['ncoor'],dtype=torch.bool,device=device)
    # Adapt the candidate chunk to the observation/trial count.
    adaptive=max(64,int(12_000_000/max(1,len(use)*obs.azimuth.shape[1])))
    chunk=max(64,min(cfg.chunk_size,adaptive))
    # Chunk candidates to bound memory: O(nobs*nmc*chunk).
    for lo in range(0,grid['ncoor'],chunk):
        hi=min(grid['ncoor'],lo+chunk)
        pb1=torch.tensordot(xyz,b1[:,lo:hi],dims=([0],[0]))
        pb3=torch.tensordot(xyz,b3[:,lo:hi],dims=([0],[0]))
        predneg=(pb1<0)!=(pb3<0)
        qmiss=(predneg != (p<0)[:,None,None])*torch.abs(p)[:,None,None]
        fit=qmiss.sum(dim=0)
        qmax=torch.maximum(fit.min(dim=1).values+float(nextra),torch.tensor(float(ntotal),device=device,dtype=dtype))
        good=(fit<=qmax[:,None]).any(dim=0)
        accepted[lo:hi]=good
    idx=torch.where(accepted)[0].detach().cpu().numpy()
    if len(idx)>cfg.maxout:
        rng=np.random.default_rng(cfg.seed)
        idx=np.sort(rng.choice(idx,cfg.maxout,replace=False))
    return GridSearchResult(grid['b3'][:,idx].copy(),grid['b1'][:,idx].copy(),idx,'torch',int(grid['ncoor']),len(idx))

def search(obs: ObservationSet, cfg: HashConfig=HashConfig()) -> GridSearchResult:
    return search_torch(obs,cfg) if cfg.backend=='torch' else search_numpy(obs,cfg)
