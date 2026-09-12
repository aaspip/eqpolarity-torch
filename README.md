
**EQpolarity**
======

## Description

**EQpolarity** package is a deep-learning-based package for determining earthquake first-motion polarity

## Reference

	Chen Y, Saad OM, Savvaidis A, Zhang F, Chen Y, Huang D, Li H, Zanjani FA, 2024, Deep learning for P-wave first-motion polarity determination and its application in focal mechanism inversion. IEEE Transactions on Geoscience and Remote Sensing, 62, 5917411.

BibTeX:

	@article{eqpolarity,
	  title={Deep learning for P-wave first-motion polarity determination and its application in focal mechanism inversion},
	  author={Yangkang Chen and Omar M. Saad and Alexandros Savvaidis and Fangxue Zhang and Yunfeng Chen and Dino Huang and Huijian Li and Farzaneh Aziz Zanjani},
	  journal={IEEE Transactions on Geoscience and Remote Sensing},
	  year={2024},
	  volume={62},
	  number={1},
	  pages={5917411},
	  doi={10.1109/TGRS.2024.3407060}
	}
 
-----------
## Copyright
    Developers of the EQpolarity package, 2021-present
-----------

## License
    MIT License

-----------

## Install

Install the appropriate CUDA-enabled PyTorch build for your system from the official PyTorch installation instructions, followed by the remaining dependencies

	pip install numpy scipy h5py matplotlib==3.8.0 scikit-learn==1.2.2 seaborn==0.13.2

Then install eqpolarity-torch using the latest version

    git clone https://github.com/chenyk1990/eqpolarity-torch
    cd eqpolarity-torch
    pip install -v -e .

Or, if you already have a local copy of the package

    cd /path/to/eqpolarity-torch
    python -m pip install -e .

No TensorFlow installation is required for normal EQpolarity-torch model loading, inference, plotting, weight conversion, or PyTorch transfer learning.

-----------
## Examples
# Texas Data Example
https://github.com/aaspip/eqpolarity-torch/tree/main/data/TexasData

-----------
## Development
    The development team welcomes voluntary contributions from any open-source enthusiast. 
    If you want to make contribution to this project, feel free to contact the development team. 

-----------
## Contact
    Regarding any questions, bugs, developments, or collaborations, please contact  
    Yangkang Chen
    chenyk2016@gmail.com

-----------
## NOTES:


### PyTorch version

**eqpolarity-torch** is a faithful PyTorch port of the TensorFlow/Keras **EQpolarity** compact convolutional transformer (CCT) for P-wave first-motion polarity classification.

### What is preserved exactly

The source EQpolarity model takes a 600-sample, one-component waveform centered on the P arrival. Its tokenizer has two `Conv1D(200,kernel=4,padding='same',use_bias=False) -> ReLU -> MaxPool1D(3,stride=2,padding='same')` stages, producing 150 x 200 tokens. Four transformer blocks use LayerNorm, four-head Keras MultiHeadAttention with **key_dim=200 per head**, stochastic depth 0..0.1, and a two-layer 200-unit GELU MLP. A final LayerNorm, flatten, dropout and sigmoid Dense(1) produce P(Down). Labels are 0=Up and 1=Down.

The PyTorch port intentionally implements TensorFlow `SAME` padding rather than relying on PyTorch defaults, because the even convolution kernel and stride-2 max-pooling otherwise shift the waveform relative to the P arrival. It also uses a custom attention module because `torch.nn.MultiheadAttention(embed_dim=200,num_heads=4)` is not equivalent to the Keras layer used here: the original has 200 dimensions **per head**, an 800-dimensional internal Q/K/V representation.

### Models

Two original `.h5` files are included and can be selected by name:

```python
from eqpolarity_torch import load_model, predict

model = load_model("scsn")   # California/SCSN pretrained model
model = load_model("texas")  # Texas 10% transfer-learning model

classes, p_down = predict(model, waveforms)  # waveforms: (N,600,1)
```

`load_model()` prefers the converted `.pt` checkpoint if present; otherwise it reads the Keras `.h5` directly with `h5py` and maps every tensor into the PyTorch architecture.

The two released model-weight files are

    best_weigths_Binary_SCSN_Best.h5
    best_weigths_Binary_Texas_Transfer10.h5

The first corresponds to the California/SCSN pretrained model and the second to the Texas 10% transfer-learning model.

### Torch-based examples

The PyTorch package includes the following examples:

* `01_predict_synthetic.py`: smoke test and plotting with bundled generated illustration data.
* `02_compare_tensorflow_torch.py`: strict TensorFlow/PyTorch numerical parity benchmark for validating the one-time weight port.
* `03_texas_transfer_learning.py`: PyTorch version of the original 10% Texas fine-tuning demo.
* `04_convert_weights.py`: inspect an original Keras HDF5 file and save a `.pt` checkpoint.
* `05_predict_texas_data.py`: reproduce Texas picking metrics when the six original Texas `.npy` chunks are available.

The Torch-based notebooks reproduce the original model-loading/confusion-matrix and Texas 10% transfer-learning workflows while keeping the original visualization style.

### Porting notes

The supplied HDF5 checkpoints contain 2 convolution kernels, 9 LayerNorms, 4 MultiHeadAttention modules, 8 transformer-MLP Dense layers, and the final 30000-to-1 classifier. The importer follows Keras `layer_names` metadata rather than hard-coding numeric suffixes because the SCSN and Texas files use different generated layer numbers.

Tensor transforms are:

* Conv1D kernel `(K, Cin, Cout)` -> PyTorch `(Cout, Cin, K)`.
* Dense kernel `(Cin, Cout)` -> PyTorch `(Cout, Cin)`.
* Keras MHA Q/K/V and output projection tensors retain their native multidimensional shapes and are evaluated with explicit `einsum`, avoiding lossy/reordered conversion.

### Texas preprocessing

For real application, follow the published/source workflow: 6 s around P (3 s before and after), 100 Hz, detrend, 1-20 Hz bandpass, and normalize the waveform before inference. This package does not silently filter already prepared arrays.


-----------
## Gallery
The gallery figures of the eqpolarity package can be found at
    https://github.com/chenyk1990/gallery/tree/main/eqpolarity

Each figure in the gallery directory corresponds to a DEMO script in the "demo" directory. These gallery figures are also presented below. 

DEMO1 
The following figures show an example confusion matrix comparison before/after transfer learning. Generated by [examples/test_texas_transferlearning.py](https://github.com/aaspip/eqpolarity-torch/blob/main/examples/test_texas_transferlearning.py)

<img src='https://github.com/chenyk1990/gallery/blob/main/eqpolarity/Conf_Matrix_before_transferlearning.png' alt='Slicing' width=480/>
<img src='https://github.com/chenyk1990/gallery/blob/main/eqpolarity/Conf_Matrix_after_transferlearning.png' alt='Slicing' width=480/>

DEMO2
The following figures show an example of plotting waveforms and polarity labels for the Texas dataset. Generated by [examples/test_plot_waveforms_and_polarity.py](https://github.com/aaspip/eqpolarity-torch/blob/main/examples/test_plot_waveforms_and_polarity.py)

<img src='https://github.com/chenyk1990/gallery/blob/main/eqpolarity/test_plot_waveforms_and_polarity.png' alt='Slicing' width=480/>

-----------
## PyHASH focal-mechanism module

`eqpolarity-torch` now also includes **PyHASH**, an installable focal-mechanism module derived from the SKHASH/HASH workflow. The purpose is to connect EQPolarity first-motion predictions directly to focal-mechanism inversion while retaining reproducibility with the published SKHASH examples.

After installing `eqpolarity-torch`, both modules are available:

```python
from eqpolarity_torch import load_model, predict
from pyhash import HashConfig, ObservationSet, solve
```

A SKHASH-compatible command-line interface is installed as well:

```bash
pyhash run examples/pyhash/skhash_reference/hash1/control_file.txt \
    --cwd examples/pyhash/skhash_reference
```

PyHASH adds a bounded-memory grid search, adaptive chunking for large composite mechanisms, cached direction grids, an optional Torch backend for polarity-only inversion, typed configuration, and direct Python APIs. The original HASH/SKHASH example inputs are included under `examples/pyhash/skhash_reference/`, with reproduction and benchmark scripts under `examples/pyhash/`.

See [`PYHASH_REPORT.md`](PYHASH_REPORT.md) for architecture, validation results, installation, and benchmark details.


DEMO3
The following figures show an example (waveform QC and final product) of end-to-end focal mechanism estimation using the EQPolarity-torch package. Generated by [examples/07_texnet_eqpolarity_focal_mechanism.py](https://github.com/aaspip/eqpolarity-torch/blob/main/examples/07_texnet_eqpolarity_focal_mechanism.py)

<img src='https://github.com/chenyk1990/gallery/blob/main/eqpolarity/texnet2022wmmd_eqpolarity_waveform_qc.png' alt='Slicing' width=480/>
<img src='https://github.com/chenyk1990/gallery/blob/main/eqpolarity/texnet2022wmmd_pyhash_focal_mechanism.png' alt='Slicing' width=480/>
