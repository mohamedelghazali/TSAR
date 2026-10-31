from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPUTE = ROOT / "rules" / "compute"

def test_files_present():
    for name in ["serverless.md", "confidential-computing.md"]:
        assert (COMPUTE / name).exists()

def test_serverless_forbids_star_iam():
    text = (COMPUTE / "serverless.md").read_text()
    assert '`*` in IAM roles' in text or "*` in IAM roles" in text or "no `*` actions" in text

def test_confidential_requires_attestation():
    text = (COMPUTE / "confidential-computing.md").read_text()
    assert "attestation" in text.lower()
