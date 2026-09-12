#!/usr/bin/env python3
"""Reproduce the five HASH-driver compatibility examples (paper Fig. 5).

Runs the bundled SKHASH-compatible engine in isolated temporary folders,
compares preferred mechanisms with the reference outputs shipped by SKHASH,
and creates a paper-style beachball comparison figure.
"""
from __future__ import annotations
import argparse, shutil, subprocess, sys, tempfile, time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyhash.plotting import beach

HERE=Path(__file__).resolve().parent
REFROOT=HERE/'skhash_reference'
EXPECTED=HERE/'reference_outputs'

def angular_delta(a,b):
    return np.abs((np.asarray(a)-np.asarray(b)+180)%360-180)

def run_one(driver:int):
    name=f'hash{driver}'
    with tempfile.TemporaryDirectory(prefix=f'pyhash_{name}_') as td:
        td=Path(td); shutil.copytree(REFROOT/name,td/name)
        # velocity models are referenced by hash2/3/4 in sibling dir
        if (REFROOT/'velocity_models').exists(): shutil.copytree(REFROOT/'velocity_models',td/'velocity_models')
        t0=time.perf_counter()
        env=dict(__import__('os').environ); env['PYTHONPATH']=str(HERE.parents[1]/'src')+__import__('os').pathsep+env.get('PYTHONPATH',''); cp=subprocess.run([sys.executable,'-m','pyhash.legacy_cli',f'{name}/control_file.txt'],cwd=td,text=True,capture_output=True,check=True,env=env)
        runtime=time.perf_counter()-t0
        got=pd.read_csv(td/name/'OUT'/'out.txt')
    exp=pd.read_csv(EXPECTED/name/'out.txt')
    m=got.merge(exp,on='event_id',suffixes=('_pyhash','_skhash'))
    errs=pd.DataFrame({
        'event_id':m.event_id,
        'dstrike':angular_delta(m.strike_pyhash,m.strike_skhash),
        'ddip':np.abs(m.dip_pyhash-m.dip_skhash),
        'drake':angular_delta(m.rake_pyhash,m.rake_skhash),
    })
    return got,exp,errs,runtime,cp.stdout

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='pyhash_hash_drivers.png'); ap.add_argument('--csv',default='pyhash_hash_driver_benchmark.csv'); ap.add_argument('--drivers',default='1,2,3,4,5',help='comma-separated HASH drivers'); args=ap.parse_args(); drivers=[int(x) for x in args.drivers.split(',') if x.strip()]
    allres={}; rows=[]
    for d in drivers:
        got,exp,err,rt,_=run_one(d); allres[d]=(got,exp)
        rows.append({'driver':d,'events':len(got),'runtime_s':rt,'max_dstrike_deg':err.dstrike.max(),'max_ddip_deg':err.ddip.max(),'max_drake_deg':err.drake.max(),'mean_sdr_abs_deg':err[['dstrike','ddip','drake']].to_numpy().mean()})
        print(f'HASH driver {d}: {len(got)} mechanisms; runtime={rt:.2f}s; max SDR deltas=({err.dstrike.max():.3g},{err.ddip.max():.3g},{err.drake.max():.3g}) deg')
    pd.DataFrame(rows).to_csv(args.csv,index=False)

    # Fig. 5-style layout: event rows, driver columns; black=PyHASH, magenta=reference SKHASH.
    ids=[]
    for d in drivers: ids.extend(allres[d][0].event_id.astype(str).tolist())
    ids=list(dict.fromkeys(ids))
    fig,axes=plt.subplots(len(ids),len(drivers),figsize=(2*len(drivers),max(12,len(ids)*0.72)),squeeze=False)
    for j,d in enumerate(drivers):
        got,exp=allres[d]; gd=got.set_index(got.event_id.astype(str)); ed=exp.set_index(exp.event_id.astype(str))
        for i,eid in enumerate(ids):
            ax=axes[i,j]; ax.set_xlim(-1.08,1.08);ax.set_ylim(-1.08,1.08);ax.set_aspect('equal');ax.axis('off')
            if eid in ed.index:
                r=ed.loc[eid]; ax.add_collection(beach(r.strike,r.dip,r.rake,facecolor='none',bgcolor='none',edgecolor='m',linewidth=1.0,zorder=1))
            if eid in gd.index:
                r=gd.loc[eid]; ax.add_collection(beach(r.strike,r.dip,r.rake,facecolor='none',bgcolor='none',edgecolor='k',linewidth=0.8,zorder=2))
            if j==0: ax.text(-1.18,0,eid,ha='right',va='center',fontsize=6)
            if i==0: ax.set_title(str(d),fontsize=9)
    fig.suptitle('PyHASH reproduction of SKHASH/HASH driver examples\nblack: PyHASH compatibility result; magenta: packaged SKHASH reference',fontsize=11)
    fig.text(0.5,0.005,'HASH driver',ha='center'); fig.tight_layout(rect=(0.06,0.02,1,0.97)); fig.savefig(args.out,dpi=220,bbox_inches='tight'); plt.close(fig)
    print('Wrote',args.out,'and',args.csv)
if __name__=='__main__': main()
