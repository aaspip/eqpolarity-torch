#!/usr/bin/env python3
"""Minimal integration pattern: EQPolarity probabilities -> weighted PyHASH observations."""
import numpy as np
from pyhash import HashConfig,ObservationSet,solve
# In a real workflow, p_down comes from eqpolarity_torch.predict(...).
rng=np.random.default_rng(42); n=48
az=np.linspace(0,352,n); takeoff=rng.uniform(25,155,n); p_down=rng.uniform(0.02,0.98,n)
# EQPolarity convention: p_down > .5 is Down.  Weight by confidence in [0,1].
pol=np.where(p_down>=.5,-1.,1.) * np.abs(2*p_down-1)
obs=ObservationSet(az,takeoff,pol)
mech,raw,pol_agree,_=solve(obs,HashConfig(nmc=1,maxout=500,backend='numpy'))
print(mech.head())
