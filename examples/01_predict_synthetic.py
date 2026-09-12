from pathlib import Path
from eqpolarity_torch import load_model, predict
from eqpolarity_torch.data import make_synthetic_polarity
from eqpolarity_torch.plot import plot_waveforms

ROOT=Path(__file__).resolve().parents[1]
x,y=make_synthetic_polarity(n=8)
for name in ["scsn","texas"]:
    model=load_model(name,models_dir=ROOT/"models",device="cpu")
    pred,prob=predict(model,x,batch_size=8)
    print(name, "probabilities:", prob.round(6))
    print(name, "classes      :", pred)
    plot_waveforms(x,y,prob,n=5,path=ROOT/f"synthetic_{name}.png")
