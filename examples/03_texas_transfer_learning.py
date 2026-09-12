"""Transfer-learning demo mirroring the original 10% Texas workflow."""
import argparse
from pathlib import Path
import numpy as np
import torch
from eqpolarity_torch import load_model, finetune, predict

p=argparse.ArgumentParser()
p.add_argument("--data-dir",required=True,help="contains datall_Texas1.npy...6.npy and polall_Texas.npy")
p.add_argument("--models-dir",default=str(Path(__file__).resolve().parents[1]/"models"))
p.add_argument("--out",default="texas_transfer10_torch.pt")
p.add_argument("--seed",type=int,default=42)
a=p.parse_args(); d=Path(a.data_dir)
x=np.concatenate([np.load(d/f"datall_Texas{i}.npy") for i in range(1,7)],axis=0).astype(np.float32)
y=np.load(d/"polall_Texas.npy").reshape(-1).astype(np.int64)
rng=np.random.default_rng(a.seed); idx=rng.permutation(len(x)); n=max(1,int(.10*len(x)))
sub=idx[:n]
model=load_model("scsn",models_dir=a.models_dir)
model,hist=finetune(model,x[sub],y[sub],epochs=50,batch_size=128,lr=1e-3,val_fraction=.1,patience=5)
pred,prob=predict(model,x,batch_size=512)
print("full-dataset illustrative accuracy:",float((pred==y).mean()))
torch.save({"state_dict":model.cpu().state_dict(),"history":hist},a.out)
print("saved",a.out)
