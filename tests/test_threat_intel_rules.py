from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TI = ROOT / "rules" / "threat-intel"

def test_files_present():
    for name in ["stix-taxii.md", "ioc-integration.md",
                 "detection-engineering.md", "threat-hunting.md"]:
        assert (TI / name).exists()

def test_stix_requires_tlp():
    text = (TI / "stix-taxii.md").read_text()
    assert "TLP" in text
    assert "TLP:RED" in text
