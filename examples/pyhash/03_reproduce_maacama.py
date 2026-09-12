#!/usr/bin/env python3
"""Plot/reproduce the Maacama composite mechanisms from SKHASH paper Fig. 4.

By default this script plots the packaged SKHASH reference output immediately.
Use ``--recompute`` to rerun the full composite inversion with PyHASH first.
The recomputation is intentionally opt-in because this is a very large
polarity-only grid search (thousands of observations) and can take minutes.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import matplotlib.pyplot as plt
import pandas as pd

from pyhash.plotting import beach

HERE = Path(__file__).resolve().parent
REF = HERE / "skhash_reference"


def _run_maacama() -> pd.DataFrame:
    """Run the Maacama control file in an isolated temporary directory."""
    with tempfile.TemporaryDirectory(prefix="pyhash_maacama_") as td0:
        td = Path(td0)
        shutil.copytree(REF / "maacama", td / "maacama")
        shutil.copytree(REF / "velocity_models", td / "velocity_models")

        env = dict(os.environ)
        src = str(HERE.parents[1] / "src")
        env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")

        cmd = [
            sys.executable,
            "-m",
            "pyhash.legacy_cli",
            "maacama/control_file.txt",
        ]
        print("Recomputing Maacama composite mechanisms...")
        print("This is a large benchmark and may take several minutes.")

        cp = subprocess.run(
            cmd,
            cwd=td,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )
        if cp.stdout:
            print(cp.stdout, end="" if cp.stdout.endswith("\n") else "\n")
        if cp.returncode != 0:
            raise RuntimeError(
                f"PyHASH Maacama run failed with return code {cp.returncode}."
            )

        return pd.read_csv(td / "maacama" / "OUT" / "out.csv")


def _reference_maacama() -> pd.DataFrame:
    path = REF / "maacama" / "OUT" / "out.csv"
    if not path.exists():
        raise FileNotFoundError(f"Reference output not found: {path}")
    print(f"Using packaged SKHASH reference output: {path}")
    return pd.read_csv(path)


def _plot(df: pd.DataFrame, out: Path, show: bool) -> None:
    n = len(df)
    fig, axs = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axs = [axs]

    for ax, (_, r) in zip(axs, df.iterrows()):
        strike = float(r["strike"])
        dip = float(r["dip"])
        rake = float(r["rake"])
        ax.set_xlim(-1.08, 1.08)
        ax.set_ylim(-1.08, 1.08)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_collection(
            beach(
                strike,
                dip,
                rake,
                facecolor=".7",
                bgcolor="white",
                edgecolor="k",
            )
        )
        ax.set_title(
            f"Composite {r['event_id']}\n"
            f"S={strike:.1f} D={dip:.1f} R={rake:.1f} ({r['quality']})"
        )

    fig.suptitle("Maacama composite focal mechanisms")
    fig.tight_layout()
    fig.savefig(out, dpi=220, bbox_inches="tight")
    print(df[["event_id", "strike", "dip", "rake", "quality"]].to_string(index=False))
    print(f"Wrote {out}")
    if show:
        plt.show()
    else:
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("pyhash_maacama.png"))
    ap.add_argument(
        "--recompute",
        action="store_true",
        help="rerun the full PyHASH Maacama inversion instead of plotting the packaged reference output",
    )
    ap.add_argument(
        "--no-show",
        action="store_true",
        help="save the figure without opening the Matplotlib window",
    )
    args = ap.parse_args()

    df = _run_maacama() if args.recompute else _reference_maacama()
    _plot(df, args.out, show=not args.no_show)


if __name__ == "__main__":
    main()
