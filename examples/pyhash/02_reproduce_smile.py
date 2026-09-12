#!/usr/bin/env python3
"""Reproduce the SKHASH 'smile' quality/misfit example (paper Fig. 3)."""
from __future__ import annotations
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from pyhash.plotting import takeoff_az2xy
HERE=Path(__file__).resolve().parent; REF=HERE/'skhash_reference'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='pyhash_smile.png'); args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='pyhash_smile_') as td:
        td=Path(td); shutil.copytree(REF/'smile',td/'smile')
        cp=subprocess.run([sys.executable,'-m','pyhash.legacy_cli','smile/control_file.txt'],cwd=td,text=True,capture_output=True,check=True,env={**__import__('os').environ,'PYTHONPATH':str(HERE.parents[1]/'src')+__import__('os').pathsep+__import__('os').environ.get('PYTHONPATH','')})
        info=pd.read_csv(td/'smile/OUT/out_polinfo.csv'); mech=pd.read_csv(td/'smile/OUT/out.csv')
    fig,axs=plt.subplots(1,2,figsize=(10,4.8))
    for ax in axs:
        t=np.linspace(0,2*np.pi,400); ax.plot(np.cos(t),np.sin(t),'k-',lw=.7); ax.set_aspect('equal');ax.axis('off'); ax.set_xlim(-1.08,1.08);ax.set_ylim(-1.08,1.08)
    pol=info[np.isfinite(info.p_polarity)].copy(); xy=takeoff_az2xy(pol.takeoff.to_numpy(),pol.azimuth.to_numpy()); x,y=xy[:,0],xy[:,1]
    good=pol.pol_agreement.fillna(0).to_numpy()>0.5; up=pol.p_polarity.to_numpy()>0
    for mask,marker,fc,label in [(good&up,'^','k','Up consistent'),((~good)&up,'^','magenta','Up inconsistent'),(good&(~up),'v','white','Down consistent'),((~good)&(~up),'v','magenta','Down inconsistent')]:
        axs[0].scatter(x[mask],y[mask],marker=marker,s=30,facecolors=fc,edgecolors='k',linewidths=.4,label=label)
    axs[0].legend(loc='lower left',fontsize=7); axs[0].set_title('(a) P-wave polarities')
    sp=info[np.isfinite(info.sp_ratio)].copy(); xy=takeoff_az2xy(sp.takeoff.to_numpy(),sp.azimuth.to_numpy()); x,y=xy[:,0],xy[:,1]; diff=sp.sp_diff.to_numpy(float)
    sc=axs[1].scatter(x,y,c=diff,s=25+55*np.abs(diff)/max(np.nanmax(np.abs(diff)),1e-8),cmap='viridis',vmin=-.05,vmax=.05,edgecolors='k',linewidths=.2)
    fig.colorbar(sc,ax=axs[1],label='log10(S/P) misfit'); axs[1].set_title('(b) S/P ratios')
    m=mech.iloc[0]; fig.suptitle(f"PyHASH smile reproduction: strike={m.strike:.1f}, dip={m.dip:.1f}, rake={m.rake:.1f}, quality={m.quality}")
    fig.tight_layout(); fig.savefig(args.out,dpi=220,bbox_inches='tight'); print(cp.stdout.splitlines()[-3:]); print('Wrote',args.out)
if __name__=='__main__': main()
