import argparse
from eqpolarity_torch.weights import save_torch_checkpoint, inspect_keras_h5
p=argparse.ArgumentParser(); p.add_argument("h5"); p.add_argument("pt"); a=p.parse_args()
for layer,weights in inspect_keras_h5(a.h5): print(layer, weights)
print("saved",save_torch_checkpoint(a.h5,a.pt))
