# EQPolarity -> PyTorch porting report

## Source architecture recovered

The uploaded TensorFlow source constructs a CCT classifier with input `(600,1)`, two convolution-tokenizer stages, four transformer blocks, final LayerNorm, flatten, dropout, and a one-neuron sigmoid output. The model summary embedded in the uploaded notebook reports **3,086,401 parameters**. The PyTorch implementation in this package has exactly **3,086,401 parameters**.

## HDF5 checkpoint inventory

Both supplied Keras checkpoints were inspected with `h5py`.

Each contains:

- two Conv1D kernels: `(4,1,200)` and `(4,200,200)`;
- four MultiHeadAttention modules, each with Q/K/V kernels `(200,4,200)`, Q/K/V biases `(4,200)`, output kernel `(4,200,200)`, and output bias `(200,)`;
- nine LayerNorm gamma/beta pairs, each `(200,)`;
- eight transformer MLP Dense kernels `(200,200)` plus biases `(200,)`;
- final classifier kernel `(30000,1)` plus bias `(1,)`.

The generated Keras layer suffixes differ between the SCSN and Texas checkpoints, so the converter intentionally follows the checkpoint's `layer_names` metadata and tensor roles rather than hard-coding names such as `dense_17` or `multi_head_attention_8`.

## Tensor conversion rules

- Keras Conv1D `(kernel, in, out)` -> PyTorch `(out, in, kernel)`.
- Keras Dense `(in, out)` -> PyTorch Linear `(out, in)`.
- LayerNorm gamma/beta -> PyTorch weight/bias directly.
- MHA tensors are retained in their original multidimensional shapes and evaluated by explicit `einsum` equations.

## Compatibility traps handled

1. The Keras Conv1D uses `kernel_size=4, padding='same'`. Because the kernel is even, SAME padding is asymmetric (left 1, right 2 for stride 1). A naive PyTorch padding choice shifts the tokens.
2. Keras MaxPool1D uses `pool_size=3, stride=2, padding='same'`. The port explicitly computes TensorFlow SAME padding and pads with `-inf` before max pooling.
3. The original `MultiHeadAttention(num_heads=4, key_dim=200)` uses **200 dimensions per head**, not a total embedding dimension of 200 split into four heads. Standard `torch.nn.MultiheadAttention(embed_dim=200,num_heads=4)` would therefore be architecturally wrong.
4. The source MLP applies GELU and dropout after both Dense(200) layers.
5. At inference, stochastic depth and dropout are disabled exactly as in Keras `predict()`.

## Validation performed here

- Both supplied `.h5` checkpoints load successfully into the PyTorch network.
- Both were converted to `.pt` checkpoints.
- Forward inference succeeds for both models and returns finite probabilities in `[0,1]`.
- PyTorch parameter count exactly matches the TensorFlow notebook summary: **3,086,401**.
- A deterministic synthetic smoke test was run with both SCSN and Texas weights.

## TensorFlow/PyTorch numerical parity

A strict parity script is included as `examples/02_compare_tensorflow_torch.py`. It constructs the original TensorFlow model, loads the same `.h5`, runs the exact same float32 traces through both frameworks, then reports max/mean probability error and class agreement.

The current build environment is Python 3.13 and does not provide TensorFlow, so the direct TensorFlow execution could not be run here. This is why the package includes a reproducible parity script rather than claiming an unexecuted numerical equality result. Run it in the original EQPolarity Python 3.10/3.11 TensorFlow environment.

## Real Texas-data reproduction

The uploaded package references `datall_Texas1.npy ... datall_Texas6.npy` and `polall_Texas.npy`, but those arrays are not present in the uploaded ZIP. `examples/05_predict_texas_data.py` reproduces the picking/metric workflow as soon as that directory is supplied. The original demo comments expect confusion matrices approximately:

- SCSN model before Texas transfer: `[[13596, 947], [296, 8141]]`
- Texas transfer model: `[[14373, 170], [158, 8279]]`

The examples deliberately do not fabricate those real-data results when the source arrays are absent.
