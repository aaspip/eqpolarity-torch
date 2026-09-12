# PyHASH integration report

## Why PyHASH is included

`pyhash` is a focal-mechanism module bundled inside `eqpolarity-torch`. It is based on the published SKHASH/HASH workflow but reorganizes the implementation around a small importable API, typed configuration, deterministic behavior, bounded-memory grid searches, optional Torch acceleration, and explicit compatibility benchmarks.

The scientific model has **not** been changed merely to make the code look different. The compatibility path preserves SKHASH's accepted-solution criteria, mechanism averaging, quality grading, input formats, uncertainty perturbations, station reversals/corrections, and output conventions so that the SKHASH examples can be reproduced.

## Main changes relative to the uploaded SKHASH package

1. **Package-safe imports.** The original executable imports a top-level `functions` package. The compatibility implementation is namespaced under `pyhash.legacy`, so it can be installed alongside `eqpolarity_torch` without changing the working directory or `sys.path` manually.
2. **Modern API.** `HashConfig`, `ObservationSet`, `search()`, and `solve()` allow direct use from Python without writing a SKHASH control file.
3. **Memory-bounded grid search.** Large SKHASH problems can allocate arrays proportional to `n_observations × n_MonteCarlo × n_grid`. The new `fast_grid.py` performs the same acceptance logic in passes over candidate chunks. This is important for the paper's `smile` and especially composite-mechanism examples.
4. **Adaptive chunks.** Chunk size automatically contracts for large station/event families to avoid multi-GB temporary arrays.
5. **Torch backend.** Polarity-only grid search can run on CPU, CUDA, or Apple MPS. S/P-constrained inversions deliberately fall back to the exact NumPy path until the amplitude-table edge behavior is validated to the same standard.
6. **Cached mechanism grids.** Direction-cosine grids are cached by grid spacing/amplitude settings rather than recreated repeatedly in a Python process.
7. **Determinism.** The default seed remains 123 for compatibility, but is an explicit configuration field in the new API.
8. **Benchmark examples.** The original HASH 1-5, `smile`, Maacama, NCSN, QuakeML, and velocity-model example data are bundled under `examples/pyhash/skhash_reference/`.

## Verified in this build

### HASH driver 1

The rewritten compatibility runner produced all 24 mechanisms and matched the packaged SKHASH preferred strike/dip/rake values exactly (maximum difference 0 degrees).

### `smile`

The memory-bounded S/P implementation reproduced the packaged preferred solution exactly:

- strike = 360.0°
- dip = 90.0°
- rake = -175.0°
- quality = A

All numeric columns in the main output row matched the packaged reference output in the test run.

### Torch backend smoke benchmark

For a synthetic polarity-only case with 30 observations and 10 Monte-Carlo trials, NumPy and Torch returned the same 3,702 accepted mechanism vectors (accepted-set Jaccard = 1.0). On the test container the median times were about 0.81 s for the faithful NumPy path and 0.06 s for the Torch path. This is only a smoke benchmark; runtime depends strongly on CPU/GPU, grid spacing, observations, trials, and accepted-solution count.

## Installation

From the `eqpolarity-torch` repository root:

```bash
python -m pip install -e .
```

This installs both packages:

```python
import eqpolarity_torch
import pyhash
```

and the command-line entry point:

```bash
pyhash --help
```

To run an SKHASH-style control file:

```bash
pyhash run examples/pyhash/skhash_reference/hash1/control_file.txt \
  --cwd examples/pyhash/skhash_reference
```

## New Python API

For observations with known source-receiver azimuths and takeoff angles:

```python
import numpy as np
from pyhash import HashConfig, ObservationSet, solve

obs = ObservationSet(
    azimuth=np.array([10., 60., 120., 180., 240., 300., 330., 350.]),
    takeoff=np.array([45., 60., 55., 70., 65., 50., 40., 75.]),
    polarity=np.array([1., 1., -1., -1., 1., 1., -1., -1.]),
)

mech, accepted, polarity_agreement, sp_difference = solve(
    obs,
    HashConfig(nmc=1, backend="numpy"),
)
print(mech)
```

For polarity-only problems, the Torch backend can be selected with:

```python
cfg = HashConfig(backend="torch", device="auto")
```

## EQPolarity -> PyHASH integration

`EQPolarity` returns a probability of the Down class. One useful integration is to convert this to a signed confidence weight:

```python
polarity = np.where(p_down >= 0.5, -1.0, 1.0) * np.abs(2.0*p_down - 1.0)
```

This maps very confident picks toward ±1 and predictions near 0.5 toward zero weight. The weighting is consistent with SKHASH's support for polarity weights in the interval -1 to 1, but the exact weighting strategy should still be validated for a particular catalog before scientific production use.

## Paper/example reproduction scripts

```bash
# Paper Fig. 5 concept: HASH drivers 1-5, PyHASH vs packaged SKHASH outputs
python examples/pyhash/01_reproduce_hash_drivers.py

# Quick exact regression test of driver 1 only
python examples/pyhash/01_reproduce_hash_drivers.py --drivers 1

# Paper Fig. 3 concept: synthetic smile polarity/S-P misfit reporting
python examples/pyhash/02_reproduce_smile.py

# Paper Fig. 4 concept: Maacama composite mechanisms
python examples/pyhash/03_reproduce_maacama.py

# Runtime/backend benchmark related to the paper's Fig. 6 efficiency discussion
python examples/pyhash/04_benchmark_backends.py

# Example of passing EQPolarity probabilities into weighted PyHASH observations
python examples/pyhash/05_eqpolarity_to_pyhash.py
```

The paper's published Figure 6 timing values were produced on 2× Intel Xeon Gold 5217 processors and should not be expected to reproduce numerically on another machine. The included backend benchmark therefore reproduces the *comparison experiment*, not those machine-specific wall-clock values.

## Important compatibility note

The package contains a rewritten public API and optimized grid-search code, plus a namespaced compatibility implementation of the remaining SKHASH readers, quality-control routines, output writers, and plotting routines. This design is intentional: it makes the published examples reproducible while allowing high-risk computational components to be replaced and benchmarked incrementally instead of silently changing scientific behavior.
