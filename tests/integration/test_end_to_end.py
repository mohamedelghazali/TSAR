"""End-to-end: scaffold a project, integrate TSAR, verify enforcement."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

def test_precommit_blocks_secret(tmp_path):
    # scaffold
    subprocess.run(["git", "init", str(tmp_path)], check=True)
    hook_src = ROOT / "integrations" / "git-hooks" / "pre-commit"
    hook_dst = tmp_path / ".git" / "hooks" / "pre-commit"
    hook_dst.write_text(hook_src.read_text())
    hook_dst.chmod(0o755)

    # vendor TSAR locally
    tsar_dir = tmp_path / ".tsar"
    tsar_dir.mkdir()
    (tsar_dir / "skills").symlink_to(ROOT / "skills")

    # stage a secret
    fake_key = "AKIAIOS" + "FODNN7EXAMPLE"
    (tmp_path / "bad.py").write_text(f'K = "{fake_key}"\n')
    subprocess.run(["git", "-C", str(tmp_path), "add", "bad.py"], check=True)

    env = {"TSAR_DIR": str(tsar_dir), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    result = subprocess.run([str(hook_dst)], cwd=str(tmp_path), env=env,
                            capture_output=True, text=True)
    assert result.returncode != 0, result.stdout + result.stderr

def test_manifest_and_rules_consistent():
    import yaml
    data = yaml.safe_load((ROOT / "manifest.yaml").read_text())
    for group, files in data["active_files"].items():
        for rel in files:
            assert (ROOT / rel).exists(), f"missing {rel}"
