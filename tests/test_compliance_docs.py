"""Verify compliance mappings reference real rule files."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
COMPLIANCE = ROOT / "docs" / "compliance"

FRAMEWORKS = ["soc2.md", "iso27001.md", "pci-dss.md", "hipaa.md", "gdpr.md"]

def test_frameworks_present():
    for name in FRAMEWORKS:
        assert (COMPLIANCE / name).exists(), f"missing {name}"

def test_frameworks_reference_valid_rules():
    missing = []
    for name in FRAMEWORKS:
        text = (COMPLIANCE / name).read_text()
        for ref in re.findall(r"(rules/[\w\-/]+\.md)", text):
            if not (ROOT / ref).exists():
                missing.append(f"{name}: {ref}")
    assert not missing, "broken references:\n" + "\n".join(missing)
