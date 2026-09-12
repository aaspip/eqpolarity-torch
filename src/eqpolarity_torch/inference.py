from __future__ import annotations
from pathlib import Path
import numpy as np
import torch
from .model import EQPolarityCCT
from .weights import load_keras_h5, load_torch_checkpoint, resolve_model_path


def load_model(model_name="texas", weights=None, models_dir=None, device=None):
    device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    model = EQPolarityCCT()
    path = Path(weights) if weights else resolve_model_path(model_name, models_dir)
    if path.suffix.lower() in {".h5", ".hdf5"}:
        load_keras_h5(model, path)
    else:
        load_torch_checkpoint(model, path)
    return model.to(device).eval()


def predict_proba(model, waveforms, batch_size=512, device=None):
    x = np.asarray(waveforms, dtype=np.float32)
    if x.ndim == 2:
        x = x[...,None]
    dev = torch.device(device or next(model.parameters()).device)
    out=[]
    model.eval()
    with torch.inference_mode():
        for i in range(0,len(x),batch_size):
            y = model(torch.from_numpy(x[i:i+batch_size]).to(dev)).squeeze(-1)
            out.append(y.cpu().numpy())
    return np.concatenate(out)


def predict(model, waveforms, threshold=0.5, **kwargs):
    p = predict_proba(model, waveforms, **kwargs)
    return (p >= threshold).astype(np.int64), p
