from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOR = ROOT / "rules" / "forensics"

def test_files_present():
    for name in ["acquisition.md", "chain-of-custody.md", "analysis.md"]:
        assert (FOR / name).exists()

def test_acquisition_order_of_volatility():
    text = (FOR / "acquisition.md").read_text()
    assert "Order of Volatility" in text
    assert "Memory" in text
    assert "Disk" in text

def test_chain_of_custody_requires_hash():
    text = (FOR / "chain-of-custody.md").read_text()
    assert "SHA-256" in text
