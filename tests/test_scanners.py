"""Test suite: verify TSAR scanners detect known patterns."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)

def test_secret_scanner_detects_aws_key(tmp_path):
    f = tmp_path / "bad.py"
    fake_key = "AKIAIOS" + "FODNN7EXAMPLE"
    f.write_text(f'AWS_KEY = "{fake_key}"\n')
    r = run([sys.executable, "skills/secret-scanner/scanner.py", str(tmp_path)])
    assert r.returncode == 1, "scanner must block on AWS key"
    assert "aws_key" in r.stdout

def test_secret_scanner_detects_private_key(tmp_path):
    f = tmp_path / "key.pem"
    pem_header = "-----BEGIN " + "PRIVATE KEY-----"
    pem_footer = "-----END " + "PRIVATE KEY-----"
    f.write_text(f"{pem_header}\nAAAA\n{pem_footer}\n")
    r = run([sys.executable, "skills/secret-scanner/scanner.py", str(tmp_path)])
    assert r.returncode == 1
    assert "private_key" in r.stdout

def test_secret_scanner_clean(tmp_path):
    f = tmp_path / "ok.py"
    f.write_text("import os\nKEY = os.environ['KEY']\n")
    r = run([sys.executable, "skills/secret-scanner/scanner.py", str(tmp_path)])
    assert r.returncode == 0

def test_secure_review_detects_sql_injection(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text('cursor.execute(f"SELECT * FROM users WHERE id = {uid}")\n')
    r = run([sys.executable, "skills/secure-review/review.py", str(tmp_path)])
    assert r.returncode == 1
    assert "sql_injection" in r.stdout

def test_secure_review_detects_eval(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("eval(user_input)\n")
    r = run([sys.executable, "skills/secure-review/review.py", str(tmp_path)])
    assert r.returncode == 1
    assert "eval_usage" in r.stdout

def test_secure_review_detects_tls_bypass(tmp_path):
    f = tmp_path / "bad.js"
    f.write_text("fetch(url, { agent: new https.Agent({ rejectUnauthorized: false }) });\n")
    r = run([sys.executable, "skills/secure-review/review.py", str(tmp_path)])
    assert r.returncode == 1
    assert "tls_disabled" in r.stdout

def test_secure_review_detects_pickle(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("import pickle\ndata = pickle.loads(user_bytes)\n")
    r = run([sys.executable, "skills/secure-review/review.py", str(tmp_path)])
    assert r.returncode == 1
    assert "pickle_load" in r.stdout

def test_crypto_inventory_detects_weak(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("from Crypto.Cipher import AES\ncipher = AES.new(key, AES.MODE_ECB)\n")
    r = run([sys.executable, "skills/crypto-inventory/inventory.py", str(tmp_path)])
    assert r.returncode == 0
    assert "AES-ECB" in r.stdout

def test_lint_rules_passes():
    r = run([sys.executable, "scripts/lint_rules.py"])
    assert r.returncode == 0, r.stdout + r.stderr

def test_manifest_all_files_exist():
    import yaml
    data = yaml.safe_load((ROOT / "manifest.yaml").read_text())
    for group, files in data["active_files"].items():
        for rel in files:
            assert (ROOT / rel).exists(), f"missing {rel}"


def test_secret_scanner_accepts_single_file_target(tmp_path):
    f = tmp_path / "single.py"
    fake_key = "AKIAIOS" + "FODNN7EXAMPLE"
    f.write_text(f'AWS_KEY = "{fake_key}"\n')
    r = run([sys.executable, "skills/secret-scanner/scanner.py", str(f)])
    assert r.returncode == 1
    assert "aws_key" in r.stdout

def test_scanners_reject_missing_path(tmp_path):
    missing = tmp_path / "does-not-exist"
    for script in ["skills/secret-scanner/scanner.py", "skills/secure-review/review.py"]:
        r = run([sys.executable, script, str(missing)])
        assert r.returncode == 2
