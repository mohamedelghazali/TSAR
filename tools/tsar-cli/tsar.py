#!/usr/bin/env python3
"""TSAR CLI: unified entry point for scan, update, verify."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS = ROOT / "skills"
SCRIPTS = ROOT / "scripts"
def run(script: Path, target: str) -> int:
    return subprocess.call([sys.executable, str(script), target])
def cmd_scan(args) -> int:
    target = args.path; rc = 0
    rc |= run(SKILLS / "secret-scanner" / "scanner.py", target)
    rc |= run(SKILLS / "secure-review" / "review.py", target)
    print(f"TSAR scan exit code: {rc}")
    return rc
def cmd_inventory(args) -> int: return run(SKILLS / "crypto-inventory" / "inventory.py", args.path)
def cmd_lint(_args) -> int: return subprocess.call([sys.executable, str(SCRIPTS / "lint_rules.py")])
def cmd_check_version(_args) -> int: return subprocess.call([sys.executable, str(SCRIPTS / "check_manifest_version.py")])
def cmd_threat_model(args) -> int: return run(SKILLS / "threat-modeler" / "model.py", args.path)
def main() -> int:
    p = argparse.ArgumentParser(prog="tsar", description="TSAR security CLI")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan", help="run secret scanner and secure review"); s.add_argument("path", nargs="?", default="."); s.set_defaults(func=cmd_scan)
    i = sub.add_parser("inventory", help="build cryptographic inventory (CBOM)"); i.add_argument("path", nargs="?", default="."); i.set_defaults(func=cmd_inventory)
    l = sub.add_parser("lint", help="validate TSAR rules"); l.set_defaults(func=cmd_lint)
    v = sub.add_parser("version", help="compare local and remote manifest version"); v.set_defaults(func=cmd_check_version)
    t = sub.add_parser("threat-model", help="generate STRIDE threat model"); t.add_argument("path", help="path to description file"); t.set_defaults(func=cmd_threat_model)
    args = p.parse_args(); return args.func(args)
if __name__ == "__main__": sys.exit(main())