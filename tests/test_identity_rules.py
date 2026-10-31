from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ID = ROOT / "rules" / "identity-federation"

def test_files_present():
    for name in ["saml.md", "oidc-federation.md",
                 "scim-provisioning.md", "idp-hardening.md"]:
        assert (ID / name).exists()

def test_saml_rejects_xsw():
    text = (ID / "saml.md").read_text()
    assert "XML Signature Wrapping" in text

def test_oidc_forbids_implicit():
    text = (ID / "oidc-federation.md").read_text()
    assert "Implicit" in text
    assert "Forbidden" in text
