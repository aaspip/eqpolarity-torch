# eqpolarity-torch

A faithful PyTorch port of the TensorFlow/Keras **EQPolarity** compact convolutional transformer (CCT) for P-wave first-motion polarity classification.

## What is preserved exactly

The source EQPolarity model takes a 600-sample, one-component waveform centered on the P arrival. Its tokenizer has two `Conv1D(200,kernel=4,padding='same',use_bias=False) -> ReLU -> MaxPool1D(3,stride=2,padding='same')` stages, producing 150 x 200 tokens. Four transformer blocks use LayerNorm, four-head Keras MultiHeadAttention with **key_dim=200 per head**, stochastic depth 0..0.1, and a two-layer 200-unit GELU MLP. A final LayerNorm, flatten, dropout and sigmoid Dense(1) produce P(Down). Labels are 0=Up and 1=Down.

The port intentionally implements TensorFlow SAME padding rather than relying on PyTorch defaults, because the even convolution kernel and stride-2 max-pooling otherwise shift the waveform relative to the P arrival. It also uses a custom attention module because `torch.nn.MultiheadAttention(embed_dim=200,num_heads=4)` is NOT equivalent to the Keras layer used here: the original has 200 dimensions **per head**, an 800-dimensional internal Q/K/V representation.

## Models

Two original `.h5` files are included and can be selected by name:

```python
from eqpolarity_torch import load_model, predict
model = load_model("scsn")   # California/SCSN pretrained model
model = load_model("texas")  # Texas 10% transfer-learning model
classes, p_down = predict(model, waveforms)  # waveforms: (N,600,1)
```

`load_model()` prefers the converted `.pt` checkpoint if present; otherwise it reads the Keras `.h5` directly with `h5py` and maps every tensor into the PyTorch architecture.

## Install

```bash
python -m pip install -e .
```

For direct TensorFlow-vs-PyTorch parity testing:

```bash
python -m pip install -e '.[benchmark]'
python examples/02_compare_tensorflow_torch.py \
  --original-repo /path/to/original/eqpolarity \
  --weights models/best_weigths_Binary_Texas_Transfer10.h5 \
  --data /path/to/datall_Texas1.npy
```

The parity script applies both frameworks to the exact same float32 traces and reports maximum/mean probability error and classification agreement.

## Examples

* `01_predict_synthetic.py`: smoke test and plotting with bundled generated illustration data.
* `02_compare_tensorflow_torch.py`: strict TensorFlow/PyTorch numerical parity benchmark.
* `03_texas_transfer_learning.py`: PyTorch version of the original 10% Texas fine-tuning demo.
* `04_convert_weights.py`: inspect an original Keras HDF5 file and save a `.pt` checkpoint.
* `05_predict_texas_data.py`: reproduce Texas picking metrics when the six original Texas `.npy` chunks are available.

## Porting notes

The supplied HDF5 checkpoints contain 2 convolution kernels, 9 LayerNorms, 4 MultiHeadAttention modules, 8 transformer-MLP Dense layers, and the final 30000-to-1 classifier. The importer follows Keras `layer_names` metadata rather than hard-coding numeric suffixes because the SCSN and Texas files use different generated layer numbers.

Tensor transforms are:

* Conv1D kernel `(K, Cin, Cout)` -> PyTorch `(Cout, Cin, K)`.
* Dense kernel `(Cin, Cout)` -> PyTorch `(Cout, Cin)`.
* Keras MHA Q/K/V and output projection tensors retain their native multidimensional shapes and are evaluated with explicit `einsum`, avoiding lossy/reordered conversion.

## Texas preprocessing

For real application, follow the published/source workflow: 6 s around P (3 s before and after), 100 Hz, detrend, 1-20 Hz bandpass, and normalize the waveform before inference. This package does not silently filter already prepared arrays.
