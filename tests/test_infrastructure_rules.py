from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INFRA = ROOT / "rules" / "infrastructure"

def test_files_present():
    for name in ["hypervisor.md", "container-orchestration.md", "virtualization.md"]:
        assert (INFRA / name).exists()

def test_hypervisor_requires_mtls():
    text = (INFRA / "hypervisor.md").read_text()
    assert "mTLS" in text
    assert "TLS 1.3" in text
