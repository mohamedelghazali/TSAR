"""Verify IAM rules reference required concepts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
IAM = ROOT / "rules" / "iam"

def test_iam_files_present():
    for name in ["design.md", "oauth2-oidc.md", "scim.md", "session-management.md"]:
        assert (IAM / name).exists()

def test_oauth_forbids_implicit():
    text = (IAM / "oauth2-oidc.md").read_text()
    assert "Implicit" in text
    assert "Forbidden" in text or "forbidden" in text

def test_oauth_requires_pkce():
    text = (IAM / "oauth2-oidc.md").read_text()
    assert "PKCE" in text
    assert "S256" in text

def test_session_rotation():
    text = (IAM / "session-management.md").read_text()
    assert "Rotate session ID on login" in text
