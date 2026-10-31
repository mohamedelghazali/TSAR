from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOV = ROOT / "rules" / "governance"

def test_files_present():
    for name in ["policy-as-code.md", "exception-management.md",
                 "vendor-risk.md", "change-management.md", "risk-assessment.md"]:
        assert (GOV / name).exists()

def test_exceptions_time_bound():
    text = (GOV / "exception-management.md").read_text()
    assert "90 days" in text
    assert "Forbidden" in text

def test_change_management_emergency():
    text = (GOV / "change-management.md").read_text()
    assert "Emergency" in text
    assert "48 hours" in text
