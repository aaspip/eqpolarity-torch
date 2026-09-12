from __future__ import annotations
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Literal

Backend = Literal['numpy','torch','legacy']

@dataclass(slots=True)
class HashConfig:
    """Typed configuration for the rewritten PyHASH solver.

    Defaults intentionally mirror SKHASH/HASH where practical, while exposing
    deterministic seeds and backend/chunk controls explicitly.
    """
    dang: float = 5.0
    nmc: int = 30
    maxout: int = 500
    badfrac: float = 0.10
    badmin: float = 2.0
    qbadfrac: float = 0.30
    qbadmin: float = 2.0
    cangle: float = 45.0
    prob_max: float = 0.20
    max_agap: float = 90.0
    max_pgap: float = 60.0
    min_polarity_weight: float = 0.10
    min_amp: float = 5e-4
    backend: Backend = 'numpy'
    device: str = 'auto'
    dtype: str = 'float32'
    chunk_size: int = 65536
    seed: int = 123
    deterministic: bool = True

    def validated(self) -> 'HashConfig':
        if not 0 < self.dang <= 45: raise ValueError('dang must be in (0,45] degrees')
        if self.nmc < 1: raise ValueError('nmc must be >= 1')
        if self.maxout < 1: raise ValueError('maxout must be >= 1')
        if self.chunk_size < 128: raise ValueError('chunk_size must be >= 128')
        if not 0 <= self.badfrac <= 1: raise ValueError('badfrac must be in [0,1]')
        if not 0 <= self.qbadfrac <= 10: raise ValueError('qbadfrac must be nonnegative')
        if self.backend not in ('numpy','torch','legacy'): raise ValueError(f'unknown backend: {self.backend}')
        return self

    def with_updates(self, **kwargs) -> 'HashConfig':
        return replace(self, **kwargs).validated()

@dataclass(slots=True)
class RunPaths:
    control_file: Path | None = None
    output_dir: Path = field(default_factory=lambda: Path('.'))
