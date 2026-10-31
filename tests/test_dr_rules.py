from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DR = ROOT / "rules" / "disaster-recovery"

def test_files_present():
    for name in ["planning.md", "testing.md", "failover.md", "communications.md"]:
        assert (DR / name).exists()

def test_tiers_defined():
    text = (DR / "planning.md").read_text()
    assert "Tier 1" in text
    assert "RTO" in text and "RPO" in text

def test_communications_timelines():
    text = (DR / "communications.md").read_text()
    assert "72 hours" in text
    assert "60 days" in text
    assert "4 business days" in text