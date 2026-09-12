#!/usr/bin/env python3
"""Benchmark faithful NumPy and optional Torch grid-search backends."""
from __future__ import annotations
import argparse,time
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from pyhash import HashConfig,ObservationSet,search_numpy,search_torch

def synthetic(nobs=60,nmc=30,seed=7):
    rng=np.random.default_rng(seed); az=rng.uniform(0,360,(nobs,nmc)); to=rng.uniform(20,160,(nobs,nmc)); pol=rng.choice([-1.,1.],nobs)
    az[:,0]=np.linspace(0,354,nobs); to[:,0]=rng.uniform(25,155,nobs)
    return ObservationSet(az,to,pol)
def bench(fn,obs,cfg,n=3):
    ts=[];res=None
    for _ in range(n): t=time.perf_counter();res=fn(obs,cfg);ts.append(time.perf_counter()-t)
    return np.median(ts),res

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='pyhash_backend_runtime.png');ap.add_argument('--nobs',type=int,default=60);ap.add_argument('--nmc',type=int,default=30);args=ap.parse_args()
    obs=synthetic(args.nobs,args.nmc); rows=[]
    cfg=HashConfig(nmc=args.nmc,maxout=100000,backend='numpy')
    t,r=bench(search_numpy,obs,cfg);rows.append({'backend':'NumPy (faithful)','seconds':t,'accepted':r.n_accepted})
    try:
        t2,r2=bench(search_torch,obs,cfg.with_updates(backend='torch')); 
        def sig(x):
            a=np.vstack((x.fault_normals,x.fault_slips)).T
            return {tuple(v) for v in np.round(a,7)}
        s1,s2=sig(r),sig(r2); inter=len(s1&s2); union=len(s1|s2); rows.append({'backend':f'Torch ({r2.backend})','seconds':t2,'accepted':r2.n_accepted}); print('accepted-mechanism Jaccard:',inter/max(union,1))
    except Exception as e: print('Torch benchmark skipped:',e)
    df=pd.DataFrame(rows);print(df);ax=df.plot.bar(x='backend',y='seconds',legend=False,rot=0);ax.set_ylabel('Median runtime (s)');ax.set_title('PyHASH grid-search backends');plt.tight_layout();plt.savefig(args.out,dpi=200);print('Wrote',args.out)
if __name__=='__main__':main()
