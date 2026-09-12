"""Import original TensorFlow/Keras EQPolarity HDF5 weights into PyTorch."""
from __future__ import annotations

from pathlib import Path
import re
import h5py
import numpy as np
import torch

from .model import EQPolarityCCT

MODEL_FILES = {
    "scsn": "best_weigths_Binary_SCSN_Best.h5",
    "california": "best_weigths_Binary_SCSN_Best.h5",
    "texas": "best_weigths_Binary_Texas_Transfer10.h5",
    "texas_transfer10": "best_weigths_Binary_Texas_Transfer10.h5",
}


def _decode(x):
    return x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x)


def _nested_dataset(group, weight_name: str):
    # Keras weight_name is relative to layer group, while HDF5 often contains
    # an additional repeated layer-name group.
    candidates = [weight_name, f"{group.name.rsplit('/',1)[-1]}/{weight_name}"]
    for c in candidates:
        if c in group:
            return np.asarray(group[c])
    # robust recursive fallback by suffix
    found = []
    def visit(name, obj):
        if isinstance(obj, h5py.Dataset) and (name.endswith(weight_name) or name.endswith(weight_name.split('/',1)[-1])):
            found.append(np.asarray(obj))
    group.visititems(visit)
    if len(found) != 1:
        raise KeyError(f"Could not uniquely resolve {weight_name!r} under {group.name}; found {len(found)}")
    return found[0]


def _layer_weights(h5: h5py.File, layer_name: str) -> dict[str, np.ndarray]:
    g = h5[layer_name]
    names = [_decode(x) for x in g.attrs.get("weight_names", [])]
    return {n: _nested_dataset(g, n) for n in names}


def inspect_keras_h5(path: str | Path) -> list[tuple[str, list[tuple[str, tuple[int,...]]]]]:
    out = []
    with h5py.File(path, "r") as h5:
        for raw in h5.attrs["layer_names"]:
            name = _decode(raw)
            ws = _layer_weights(h5, name)
            if ws:
                out.append((name, [(k, tuple(v.shape)) for k, v in ws.items()]))
    return out


def load_keras_h5(model: EQPolarityCCT, path: str | Path, strict: bool = True) -> EQPolarityCCT:
    """Load an original EQPolarity Keras save_weights(.h5) file.

    Mapping is driven by HDF5 layer metadata and tensor roles/shapes, not by
    hard-coded absolute layer numbers, so both supplied SCSN and Texas files work.
    """
    path = Path(path)
    with h5py.File(path, "r") as h5:
        layer_names = [_decode(x) for x in h5.attrs["layer_names"]]
        weighted = [(n, _layer_weights(h5, n)) for n in layer_names]
        weighted = [(n,w) for n,w in weighted if w]

        tokenizer = [(n,w) for n,w in weighted if n.startswith("cct_tokenizer")]
        norms = [(n,w) for n,w in weighted if n.startswith("layer_normalization")]
        mhas = [(n,w) for n,w in weighted if n.startswith("multi_head_attention")]
        dens = [(n,w) for n,w in weighted if n.startswith("dense")]

        if strict:
            assert len(tokenizer) == 1, len(tokenizer)
            assert len(norms) == 9, len(norms)
            assert len(mhas) == 4, len(mhas)
            assert len(dens) == 9, len(dens)

        # Tokenizer: layer metadata keeps the two conv kernels in source order.
        tw = tokenizer[0][1]
        conv_arrays = [v for k,v in tw.items() if "kernel" in k]
        if len(conv_arrays) != 2:
            raise ValueError("Expected exactly two tokenizer Conv1D kernels")
        for torch_conv, arr in zip([model.tokenizer.conv1.conv, model.tokenizer.conv2.conv], conv_arrays):
            # TF Conv1D: (kernel, in, out) -> Torch: (out, in, kernel)
            torch_conv.weight.data.copy_(torch.from_numpy(arr.transpose(2,1,0)))

        # Preserve Keras graph creation order from layer_names.
        for i in range(4):
            for norm_mod, (_,w) in zip([model.blocks[i].norm1, model.blocks[i].norm2], norms[2*i:2*i+2]):
                gamma = next(v for k,v in w.items() if "gamma" in k)
                beta = next(v for k,v in w.items() if "beta" in k)
                norm_mod.weight.data.copy_(torch.from_numpy(gamma))
                norm_mod.bias.data.copy_(torch.from_numpy(beta))
        fw = norms[-1][1]
        model.final_norm.weight.data.copy_(torch.from_numpy(next(v for k,v in fw.items() if "gamma" in k)))
        model.final_norm.bias.data.copy_(torch.from_numpy(next(v for k,v in fw.items() if "beta" in k)))

        # MHA tensors already have exactly the Keras-compatible shapes used by model.py.
        for block, (_,w) in zip(model.blocks, mhas):
            def get(role, kind):
                return next(v for k,v in w.items() if f"/{role}/" in k and kind in k)
            a = block.attn
            a.query_kernel.data.copy_(torch.from_numpy(get("query","kernel")))
            a.query_bias.data.copy_(torch.from_numpy(get("query","bias")))
            a.key_kernel.data.copy_(torch.from_numpy(get("key","kernel")))
            a.key_bias.data.copy_(torch.from_numpy(get("key","bias")))
            a.value_kernel.data.copy_(torch.from_numpy(get("value","kernel")))
            a.value_bias.data.copy_(torch.from_numpy(get("value","bias")))
            a.output_kernel.data.copy_(torch.from_numpy(get("attention_output","kernel")))
            a.output_bias.data.copy_(torch.from_numpy(get("attention_output","bias")))

        # First 8 Dense layers are MLP fc1/fc2; last Dense is 30000->1 classifier.
        for linear, (_,w) in zip(
            [m for b in model.blocks for m in (b.fc1,b.fc2)], dens[:8]
        ):
            kernel = next(v for k,v in w.items() if "kernel" in k)
            bias = next(v for k,v in w.items() if "bias" in k)
            linear.weight.data.copy_(torch.from_numpy(kernel.T))
            linear.bias.data.copy_(torch.from_numpy(bias))
        cw = dens[-1][1]
        kernel = next(v for k,v in cw.items() if "kernel" in k)
        bias = next(v for k,v in cw.items() if "bias" in k)
        if kernel.shape != (30000,1):
            raise ValueError(f"Unexpected classifier kernel shape {kernel.shape}")
        model.classifier.weight.data.copy_(torch.from_numpy(kernel.T))
        model.classifier.bias.data.copy_(torch.from_numpy(bias))

    return model


def save_torch_checkpoint(h5_path: str | Path, pt_path: str | Path) -> Path:
    model = load_keras_h5(EQPolarityCCT(), h5_path)
    payload = {
        "state_dict": model.state_dict(),
        "architecture": "EQPolarityCCT",
        "input_samples": 600,
        "source_h5": Path(h5_path).name,
    }
    pt_path = Path(pt_path)
    torch.save(payload, pt_path)
    return pt_path


def load_torch_checkpoint(model: EQPolarityCCT, path: str | Path) -> EQPolarityCCT:
    obj = torch.load(path, map_location="cpu", weights_only=False)
    state = obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj
    model.load_state_dict(state)
    return model


def resolve_model_path(model_name: str, models_dir: str | Path | None = None) -> Path:
    key = model_name.lower().replace("-","_")
    aliases = {"scsn":"scsn", "california":"scsn", "texas":"texas", "texas_transfer10":"texas"}
    if key not in aliases:
        raise ValueError(f"Unknown model {model_name!r}; choose 'scsn' or 'texas'.")
    stem = aliases[key]
    models_dir = Path(models_dir) if models_dir else Path(__file__).resolve().parents[2] / "models"
    pt = models_dir / ("eqpolarity_scsn.pt" if stem == "scsn" else "eqpolarity_texas_transfer10.pt")
    if pt.exists():
        return pt
    h5 = models_dir / MODEL_FILES[stem]
    if h5.exists():
        return h5
    raise FileNotFoundError(f"No packaged weights found in {models_dir}")
