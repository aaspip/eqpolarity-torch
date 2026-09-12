"""Data helpers matching the original 600-sample vertical-component input."""
from __future__ import annotations
import numpy as np


def normalize_trace(x, eps=1e-12):
    x = np.asarray(x, dtype=np.float32)
    m = np.max(np.abs(x), axis=-1, keepdims=True)
    return x / np.maximum(m, eps)


def make_synthetic_polarity(n=32, samples=600, p_index=300, seed=7):
    """Small illustrative dataset; labels follow EQPolarity: 0=Up, 1=Down.

    It is NOT the training dataset and is intended only for smoke tests/examples.
    """
    rng=np.random.default_rng(seed)
    t=np.arange(samples)
    x=np.empty((n,samples),np.float32)
    y=rng.integers(0,2,size=n,dtype=np.int64)
    for i,label in enumerate(y):
        noise=0.10*rng.normal(size=samples)
        # first-motion pulse with damped coda after the nominal P sample
        u=np.maximum(t-p_index,0)
        pulse=np.exp(-u/18.0)*np.sin(2*np.pi*u/24.0)
        pulse[t<p_index]=0
        sign=1.0 if label==0 else -1.0
        x[i]=noise+sign*pulse
    x=normalize_trace(x)
    return x[...,None], y
