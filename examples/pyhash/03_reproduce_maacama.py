#!/usr/bin/env python3
"""Reproduce the two Maacama composite mechanisms discussed in paper Fig. 4."""
from pathlib import Path
import argparse, shutil, subprocess, sys, tempfile
import pandas as pd, matplotlib.pyplot as plt
from pyhash.plotting import beach
HERE=Path(__file__).resolve().parent; REF=HERE/'skhash_reference'
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='pyhash_maacama.png'); args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='pyhash_maacama_') as td:
        td=Path(td); shutil.copytree(REF/'maacama',td/'maacama'); shutil.copytree(REF/'velocity_models',td/'velocity_models')
        subprocess.run([sys.executable,'-m','pyhash.legacy_cli','maacama/control_file.txt'],cwd=td,text=True,capture_output=True,check=True,env={**__import__('os').environ,'PYTHONPATH':str(HERE.parents[1]/'src')+__import__('os').pathsep+__import__('os').environ.get('PYTHONPATH','')})
        df=pd.read_csv(td/'maacama/OUT/out.csv')
    fig,axs=plt.subplots(1,len(df),figsize=(4*len(df),4));
    if len(df)==1: axs=[axs]
    for ax,(_,r) in zip(axs,df.iterrows()):
        ax.set_xlim(-1.08,1.08);ax.set_ylim(-1.08,1.08);ax.set_aspect('equal');ax.axis('off'); ax.add_collection(beach(r.strike,r.dip,r.rake,facecolor='.7',bgcolor='white',edgecolor='k')); ax.set_title(f"Composite {r.event_id}\nS={r.strike:.1f} D={r.dip:.1f} R={r.rake:.1f} ({r.quality})")
    fig.suptitle('PyHASH reproduction of Maacama composite mechanisms');fig.tight_layout();fig.savefig(args.out,dpi=220,bbox_inches='tight');print(df[['event_id','strike','dip','rake','quality']]);print('Wrote',args.out)
if __name__=='__main__':main()
