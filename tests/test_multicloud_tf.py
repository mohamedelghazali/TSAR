"""Verify multi-cloud Terraform example structure."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MC = ROOT / "examples" / "secure" / "multi-cloud"

def test_files_present():
    for name in ["federation.tf", "variables.tf", "README.md"]:
        assert (MC / name).exists()

def test_federation_uses_oidc():
    text = (MC / "federation.tf").read_text()
    assert "aws_iam_openid_connect_provider" in text
    assert "google_iam_workload_identity_pool" in text
    assert "azuread_application_federated_identity_credential" in text

def test_no_static_credentials():
    text = (MC / "federation.tf").read_text()
    assert "access_key" not in text.lower() or "access_key_id" not in text.lower()
    assert "client_secret" not in text.lower()
