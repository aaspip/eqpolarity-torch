from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt


def plot_waveforms(x, labels=None, probs=None, n=5, p_index=300, path=None):
    x=np.asarray(x)
    if x.ndim==3: x=x[...,0]
    n=min(n,len(x)); fig,axes=plt.subplots(n,1,figsize=(8,1.8*n),sharex=True)
    axes=np.atleast_1d(axes)
    for i,ax in enumerate(axes):
        ax.plot(x[i],lw=1.2); ax.axvline(p_index,ls='--',lw=.8)
        title=[]
        if labels is not None: title.append(f"label={int(labels[i])} ({'Up' if int(labels[i])==0 else 'Down'})")
        if probs is not None: title.append(f"P(Down)={float(probs[i]):.4f}")
        ax.set_title(" | ".join(title)); ax.set_yticks([])
    axes[-1].set_xlabel("Sample")
    fig.tight_layout()
    if path: fig.savefig(path,dpi=180)
    return fig
