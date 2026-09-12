from __future__ import annotations
import os, subprocess, sys
from pathlib import Path

def run_skhash_control(control_file, cwd=None, check=True):
    """Run a SKHASH control file through the bundled compatibility engine.

    The engine is namespaced inside ``pyhash`` and does not require a separate
    SKHASH installation. Relative paths are resolved from ``cwd`` exactly as in
    the original examples.
    """
    control_file=Path(control_file)
    if cwd is None: cwd=control_file.parent.parent if control_file.parent.name not in ('','.') else Path.cwd()
    cmd=[sys.executable,'-m','pyhash.legacy_cli',str(control_file if control_file.is_absolute() else control_file)]
    return subprocess.run(cmd,cwd=str(cwd),check=check,text=True,capture_output=True)
