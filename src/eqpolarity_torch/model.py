"""PyTorch implementation of the published EQPolarity CCT architecture.

Important compatibility details:
* Input shape is (batch, 600, 1), matching the TensorFlow repository.
* TensorFlow SAME padding is reproduced exactly for Conv1D(k=4,s=1)
  and MaxPool1D(k=3,s=2), including the asymmetric padding for even kernels.
* MultiHeadAttention reproduces Keras' unusual key_dim=200 PER HEAD with
  four heads, i.e. Q/K/V each have an internal width of 800 before the
  output projection returns to 200 channels.
* MLP uses GELU after BOTH Dense(200) layers, exactly as the source code.
"""
from __future__ import annotations

import math
import torch
from torch import nn
import torch.nn.functional as F


def _same_padding_1d(length: int, kernel: int, stride: int) -> tuple[int, int]:
    out = math.ceil(length / stride)
    total = max((out - 1) * stride + kernel - length, 0)
    return total // 2, total - total // 2


class TFSameConv1d(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 4):
        super().__init__()
        self.kernel_size = kernel_size
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size, stride=1,
                              padding=0, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        left, right = _same_padding_1d(x.shape[-1], self.kernel_size, 1)
        return self.conv(F.pad(x, (left, right)))


class TFSameMaxPool1d(nn.Module):
    def __init__(self, kernel_size: int = 3, stride: int = 2):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        left, right = _same_padding_1d(x.shape[-1], self.kernel_size, self.stride)
        # TensorFlow MAX_POOL SAME behaves as if padded locations were -inf.
        x = F.pad(x, (left, right), value=float("-inf"))
        return F.max_pool1d(x, self.kernel_size, self.stride, padding=0)


class Tokenizer(nn.Module):
    def __init__(self, projection_dim: int = 200):
        super().__init__()
        self.conv1 = TFSameConv1d(1, projection_dim, 4)
        self.pool1 = TFSameMaxPool1d(3, 2)
        self.conv2 = TFSameConv1d(projection_dim, projection_dim, 4)
        self.pool2 = TFSameMaxPool1d(3, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Public API follows TensorFlow: (B,T,C). Conv1d uses (B,C,T).
        x = x.transpose(1, 2)
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        return x.transpose(1, 2)  # (B,150,200)


class KerasCompatibleMHA(nn.Module):
    """Exact tensor layout of tf.keras.layers.MultiHeadAttention.

    Keras source model used num_heads=4, key_dim=200, dropout=0.2.
    Weight shapes in the .h5 files are:
      query/key/value kernel: (200, 4, 200)
      query/key/value bias:   (4, 200)
      output kernel:          (4, 200, 200)
      output bias:            (200,)
    """
    def __init__(self, input_dim: int = 200, num_heads: int = 4,
                 key_dim: int = 200, dropout: float = 0.2):
        super().__init__()
        self.num_heads = num_heads
        self.key_dim = key_dim
        self.scale = key_dim ** -0.5
        self.query_kernel = nn.Parameter(torch.empty(input_dim, num_heads, key_dim))
        self.query_bias = nn.Parameter(torch.empty(num_heads, key_dim))
        self.key_kernel = nn.Parameter(torch.empty(input_dim, num_heads, key_dim))
        self.key_bias = nn.Parameter(torch.empty(num_heads, key_dim))
        self.value_kernel = nn.Parameter(torch.empty(input_dim, num_heads, key_dim))
        self.value_bias = nn.Parameter(torch.empty(num_heads, key_dim))
        self.output_kernel = nn.Parameter(torch.empty(num_heads, key_dim, input_dim))
        self.output_bias = nn.Parameter(torch.empty(input_dim))
        self.attn_dropout = nn.Dropout(dropout)
        self.reset_parameters()

    def reset_parameters(self):
        for p in [self.query_kernel, self.key_kernel, self.value_kernel, self.output_kernel]:
            nn.init.xavier_uniform_(p.reshape(p.shape[0], -1))
        for p in [self.query_bias, self.key_bias, self.value_bias, self.output_bias]:
            nn.init.zeros_(p)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        q = torch.einsum("bti,ihd->bthd", x, self.query_kernel) + self.query_bias
        k = torch.einsum("bti,ihd->bthd", x, self.key_kernel) + self.key_bias
        v = torch.einsum("bti,ihd->bthd", x, self.value_kernel) + self.value_bias
        scores = torch.einsum("bthd,bshd->bhts", q, k) * self.scale
        weights = torch.softmax(scores, dim=-1)
        weights = self.attn_dropout(weights)
        context = torch.einsum("bhts,bshd->bthd", weights, v)
        return torch.einsum("bthd,hdo->bto", context, self.output_kernel) + self.output_bias


class DropPath(nn.Module):
    def __init__(self, drop_prob: float = 0.0):
        super().__init__()
        self.drop_prob = float(drop_prob)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self.training or self.drop_prob == 0.0:
            return x
        keep = 1.0 - self.drop_prob
        shape = (x.shape[0],) + (1,) * (x.ndim - 1)
        mask = torch.floor(keep + torch.rand(shape, dtype=x.dtype, device=x.device))
        return x * mask / keep


class TransformerBlock(nn.Module):
    def __init__(self, dim: int = 200, num_heads: int = 4, key_dim: int = 200,
                 dropout: float = 0.2, drop_path: float = 0.0):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, eps=1e-5)
        self.attn = KerasCompatibleMHA(dim, num_heads, key_dim, dropout)
        self.drop_path1 = DropPath(drop_path)
        self.norm2 = nn.LayerNorm(dim, eps=1e-5)
        self.fc1 = nn.Linear(dim, dim)
        self.fc2 = nn.Linear(dim, dim)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.drop_path2 = DropPath(drop_path)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.drop_path1(self.attn(self.norm1(x)))
        y = self.norm2(x)
        y = self.dropout1(F.gelu(self.fc1(y), approximate="none"))
        y = self.dropout2(F.gelu(self.fc2(y), approximate="none"))
        return x + self.drop_path2(y)


class EQPolarityCCT(nn.Module):
    def __init__(self, input_samples: int = 600, projection_dim: int = 200,
                 num_heads: int = 4, transformer_layers: int = 4,
                 dropout: float = 0.2, stochastic_depth_rate: float = 0.1):
        super().__init__()
        self.input_samples = input_samples
        self.projection_dim = projection_dim
        self.tokenizer = Tokenizer(projection_dim)
        rates = torch.linspace(0.0, stochastic_depth_rate, transformer_layers).tolist()
        self.blocks = nn.ModuleList([
            TransformerBlock(projection_dim, num_heads, projection_dim, dropout, rates[i])
            for i in range(transformer_layers)
        ])
        self.final_norm = nn.LayerNorm(projection_dim, eps=1e-5)
        self.final_dropout = nn.Dropout(dropout)
        # 600 -> ceil/2 -> 300 -> ceil/2 -> 150
        self.classifier = nn.Linear(150 * projection_dim, 1)

    def logits(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 2:
            x = x.unsqueeze(-1)
        if x.ndim != 3 or x.shape[1:] != (self.input_samples, 1):
            raise ValueError(f"Expected input (B,{self.input_samples},1), got {tuple(x.shape)}")
        x = self.tokenizer(x)
        for block in self.blocks:
            x = block(x)
        x = self.final_norm(x)
        x = self.final_dropout(x)
        return self.classifier(x.flatten(1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(self.logits(x))
