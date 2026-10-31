from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "rules" / "secrets"

def test_files_present():
    for name in ["vault.md", "aws-secrets-manager.md", "sops.md"]:
        assert (SEC / name).exists()

def test_vault_forbids_root_token():
    text = (SEC / "vault.md").read_text()
    assert "Root token" in text or "root token" in text

def test_aws_forbids_default_kms():
    text = (SEC / "aws-secrets-manager.md").read_text()
    assert "aws/secretsmanager" in text
