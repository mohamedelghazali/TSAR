from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LH = ROOT / "rules" / "legal-hold"

def test_files_present():
    for name in ["preservation.md", "evidence-handling.md", "privilege.md"]:
        assert (LH / name).exists()

def test_preservation_forbids_spoliation():
    text = (LH / "preservation.md").read_text()
    assert "spoliation" in text.lower()
    assert "Forbidden" in text

def test_evidence_chain_of_custody():
    text = (LH / "evidence-handling.md").read_text()
    assert "Chain of Custody" in text