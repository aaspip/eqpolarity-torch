from pathlib import Path
import numpy as np
import torch
from eqpolarity_torch.model import EQPolarityCCT
from eqpolarity_torch.weights import load_keras_h5

ROOT=Path(__file__).resolve().parents[1]
def test_forward_and_both_h5_files():
    x=torch.randn(2,600,1)
    for fn in ["best_weigths_Binary_SCSN_Best.h5","best_weigths_Binary_Texas_Transfer10.h5"]:
        m=load_keras_h5(EQPolarityCCT(),ROOT/"models"/fn).eval()
        with torch.inference_mode(): y=m(x)
        assert y.shape==(2,1)
        assert torch.isfinite(y).all()
        assert ((y>=0)&(y<=1)).all()
