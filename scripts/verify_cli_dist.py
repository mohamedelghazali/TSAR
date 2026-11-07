"""Verify TSAR CLI wheel and source distribution contents before release."""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import tarfile
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "tools" / "tsar-cli"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    dist = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT / "dist"
    project = tomllib.loads((PROJECT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    wheels = sorted(dist.glob("tsar_cli-*.whl"))
    sdists = sorted(dist.glob("tsar_cli-*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit(f"Expected exactly one wheel and one sdist; found wheels={wheels}, sdists={sdists}")

    required_modules = {"tsar.py", "lifecycle_anchor.py", "lifecycle_evidence.py"}
    dist_info = f"tsar_cli-{version}.dist-info"
    with zipfile.ZipFile(wheels[0]) as wheel:
        names = set(wheel.namelist())
        missing = required_modules - names
        if missing:
            raise SystemExit(f"Wheel is missing required modules: {sorted(missing)}")
        metadata = wheel.read(f"{dist_info}/METADATA").decode("utf-8")
        if f"Version: {version}" not in metadata:
            raise SystemExit("Wheel metadata version does not match pyproject.toml.")
        entry_points = wheel.read(f"{dist_info}/entry_points.txt").decode("utf-8")
        if "tsar = tsar:main" not in entry_points:
            raise SystemExit("Wheel is missing the tsar console entry point.")

    with tarfile.open(sdists[0], "r:gz") as archive:
        files = [Path(member.name) for member in archive.getmembers() if member.isfile()]
        members = {member.name for member in files}
        missing = (required_modules | {"pyproject.toml"}) - members
        if missing:
            raise SystemExit(f"Source distribution is missing required files: {sorted(missing)}")
        roots = {member.parts[0] for member in files if len(member.parts) > 1}
        if not any(root.endswith(f"-{version}") for root in roots):
            raise SystemExit("Source distribution root/version does not match pyproject.toml.")

    print(f"Verified TSAR CLI {version}: wheel={sha256(wheels[0])} sdist={sha256(sdists[0])}")


if __name__ == "__main__":
    main()
