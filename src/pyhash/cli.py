from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compat import run_skhash_control


def _resolve_existing_file(path: str | Path, *, base: Path) -> Path:
    """Resolve *path* against the caller's working directory before cwd changes.

    This is intentionally done in the public CLI rather than inside the legacy
    engine so a command such as

        pyhash run examples/.../hash1/control_file.txt --cwd examples/.../

    continues to refer to the control file relative to the directory from which
    ``pyhash`` was invoked, not relative to ``--cwd``.
    """
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = base / p
    p = p.resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Control file does not exist: {p}")
    return p


def _resolve_directory(path: str | Path, *, base: Path) -> Path:
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = base / p
    p = p.resolve()
    if not p.is_dir():
        raise NotADirectoryError(f"Working directory does not exist: {p}")
    return p


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="pyhash",
        description="PyHASH focal-mechanism tools bundled with eqpolarity-torch",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_parser = sub.add_parser("run", help="run an SKHASH-compatible control file")
    run_parser.add_argument("control_file", help="path to an SKHASH-compatible control file")
    run_parser.add_argument(
        "--cwd",
        default=None,
        help=(
            "working directory used to resolve paths inside the control file; "
            "relative --cwd paths are resolved from the directory where pyhash was invoked"
        ),
    )

    args = parser.parse_args(argv)

    if args.cmd == "run":
        # Capture the invocation directory once.  Both the control-file path and
        # --cwd must be interpreted relative to this directory.  Resolving the
        # control file to an absolute path *before* launching the compatibility
        # subprocess prevents --cwd from accidentally being prepended twice.
        invocation_dir = Path.cwd().resolve()

        try:
            control_file = _resolve_existing_file(args.control_file, base=invocation_dir)
            cwd = (
                _resolve_directory(args.cwd, base=invocation_dir)
                if args.cwd is not None
                else None
            )
        except (FileNotFoundError, NotADirectoryError) as exc:
            parser.error(str(exc))

        cp = run_skhash_control(control_file, cwd=cwd, check=False)
        sys.stdout.write(cp.stdout)
        sys.stderr.write(cp.stderr)
        return cp.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
