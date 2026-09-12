import argparse
from pathlib import Path
import numpy as np
from eqpolarity_torch import load_model, predict
p=argparse.ArgumentParser(); p.add_argument("--data-dir",required=True); p.add_argument("--model",choices=["scsn","texas"],default="texas"); p.add_argument("--models-dir",default=str(Path(__file__).resolve().parents[1]/"models")); p.add_argument("--threshold",type=float,default=.5); a=p.parse_args()
d=Path(a.data_dir)
x=np.concatenate([np.load(d/f"datall_Texas{i}.npy") for i in range(1,7)],axis=0).astype(np.float32)
y=np.load(d/"polall_Texas.npy").reshape(-1)
model=load_model(a.model,models_dir=a.models_dir)
pred,prob=predict(model,x,threshold=a.threshold,batch_size=512)
print("model=",a.model,"N=",len(y),"accuracy=",float((pred==y).mean()))
try:
 from sklearn.metrics import confusion_matrix,precision_score,recall_score,f1_score
 print("precision=",precision_score(y,pred),"recall=",recall_score(y,pred),"f1=",f1_score(y,pred))
 print("confusion matrix:\n",confusion_matrix(y,pred))
except ImportError: pass
