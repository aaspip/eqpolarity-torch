from __future__ import annotations
import copy
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset, random_split


def finetune(model, x, y, epochs=50, batch_size=128, lr=1e-3,
             val_fraction=0.1, patience=5, device=None, seed=42):
    """PyTorch equivalent of the original Texas transfer-learning demo."""
    dev=torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    x=np.asarray(x,dtype=np.float32)
    if x.ndim==2: x=x[...,None]
    y=np.asarray(y,dtype=np.float32).reshape(-1,1)
    ds=TensorDataset(torch.from_numpy(x),torch.from_numpy(y))
    nv=max(1,int(round(len(ds)*val_fraction))); nt=len(ds)-nv
    gen=torch.Generator().manual_seed(seed)
    train_ds,val_ds=random_split(ds,[nt,nv],generator=gen)
    train_loader=DataLoader(train_ds,batch_size=batch_size,shuffle=True)
    val_loader=DataLoader(val_ds,batch_size=batch_size,shuffle=False)
    model=model.to(dev)
    opt=torch.optim.Adam(model.parameters(),lr=lr)
    loss_fn=nn.BCEWithLogitsLoss()
    best=float('inf'); best_state=None; stale=0; history=[]
    for epoch in range(1,epochs+1):
        model.train(); tr=0.; n=0
        for xb,yb in train_loader:
            xb,yb=xb.to(dev),yb.to(dev)
            opt.zero_grad(set_to_none=True)
            loss=loss_fn(model.logits(xb),yb); loss.backward(); opt.step()
            tr += loss.item()*len(xb); n += len(xb)
        model.eval(); va=0.; vn=0
        with torch.inference_mode():
            for xb,yb in val_loader:
                xb,yb=xb.to(dev),yb.to(dev)
                loss=loss_fn(model.logits(xb),yb)
                va += loss.item()*len(xb); vn += len(xb)
        tr/=max(n,1); va/=max(vn,1); history.append((epoch,tr,va))
        print(f"epoch {epoch:03d} train_loss={tr:.6f} val_loss={va:.6f}")
        if va < best:
            best=va; best_state=copy.deepcopy(model.state_dict()); stale=0
        else:
            stale += 1
            if stale >= patience: break
    if best_state is not None: model.load_state_dict(best_state)
    return model, history
