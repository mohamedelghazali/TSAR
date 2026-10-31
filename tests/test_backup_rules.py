from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

def test_backup_files_present():
    for name in ["strategy.md", "immutability.md", "air-gap.md", "ransomware-resilience.md"]:
        assert (ROOT / "rules" / "backup" / name).exists()

def test_strategy_references_3_2_1():
    text = (ROOT / "rules" / "backup" / "strategy.md").read_text()
    assert "3-2-1-1-0" in text or "3** copies" in text

def test_immutability_compliance_mode():
    text = (ROOT / "rules" / "backup" / "immutability.md").read_text()
    assert "Compliance mode" in text

def test_air_gap_requires_two_person():
    text = (ROOT / "rules" / "backup" / "air-gap.md").read_text()
    assert "two-person" in text