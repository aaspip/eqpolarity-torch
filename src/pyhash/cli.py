from __future__ import annotations
import argparse,sys
from .compat import run_skhash_control

def main(argv=None):
    p=argparse.ArgumentParser(prog='pyhash',description='PyHASH focal-mechanism tools bundled with eqpolarity-torch')
    sub=p.add_subparsers(dest='cmd',required=True)
    r=sub.add_parser('run',help='run an SKHASH-compatible control file')
    r.add_argument('control_file'); r.add_argument('--cwd',default=None)
    args=p.parse_args(argv)
    if args.cmd=='run':
        cp=run_skhash_control(args.control_file,args.cwd,check=False)
        sys.stdout.write(cp.stdout); sys.stderr.write(cp.stderr); return cp.returncode
    return 0
