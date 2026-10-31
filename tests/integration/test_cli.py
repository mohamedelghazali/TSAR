"""Integration tests for the TSAR CLI."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CLI = ROOT / "tools" / "tsar-cli" / "tsar.py"

def run(args):
    return subprocess.run([sys.executable, str(CLI), *args],
                          capture_output=True, text=True, cwd=ROOT)

def test_cli_scan_clean(tmp_path):
    (tmp_path / "ok.py").write_text("import os\nKEY = os.environ['K']\n")
    r = run(["scan", str(tmp_path)])
    assert r.returncode == 0, r.stdout + r.stderr

def test_cli_scan_blocks_secret(tmp_path):
    fake_key = "AKIAIOS" + "FODNN7EXAMPLE"
    (tmp_path / "bad.py").write_text(f'K = "{fake_key}"\n')
    r = run(["scan", str(tmp_path)])
    assert r.returncode != 0

def test_cli_lint():
    r = run(["lint"])
    assert r.returncode == 0, r.stdout + r.stderr

def test_cli_inventory(tmp_path):
    (tmp_path / "c.py").write_text("cipher = AES.new(k, AES.MODE_ECB)\n")
    r = run(["inventory", str(tmp_path)])
    assert r.returncode == 0
    assert "AES-ECB" in r.stdout

def test_cli_threat_model(tmp_path):
    f = tmp_path / "desc.txt"
    f.write_text("Web app with login and payments.")
    r = run(["threat-model", str(f)])
    assert r.returncode == 0
    assert "STRIDE" in r.stdout
