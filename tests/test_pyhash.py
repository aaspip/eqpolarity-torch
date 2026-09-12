import numpy as np
from pyhash import HashConfig, ObservationSet, search_numpy, search_torch

def _obs(seed=2):
    r=np.random.default_rng(seed); n=12; m=2
    return ObservationSet(r.uniform(0,360,(n,m)),r.uniform(20,160,(n,m)),r.choice([-1.,1.],n))

def _signature(result):
    a=np.vstack((result.fault_normals,result.fault_slips)).T
    return {tuple(x) for x in np.round(a,6)}

def test_numpy_grid_runs():
    r=search_numpy(_obs(),HashConfig(nmc=2,maxout=100000))
    assert r.n_candidates>0 and r.fault_normals.shape[0]==3

def test_torch_matches_numpy_accepted_mechanisms():
    obs=_obs(); cfg=HashConfig(nmc=2,maxout=100000)
    a=search_numpy(obs,cfg); b=search_torch(obs,cfg.with_updates(backend='torch'))
    assert _signature(a)==_signature(b)
