from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PRIV = ROOT / "rules" / "privacy"

def test_files_present():
    for name in ["data-minimization.md", "anonymization.md",
                 "differential-privacy.md", "consent.md", "dsr.md",
                 "privacy-by-design.md"]:
        assert (PRIV / name).exists()

def test_anonymization_forbids_plain_sha():
    text = (PRIV / "anonymization.md").read_text()
    assert "Plain SHA-256" in text
    assert "HMAC-SHA-256" in text

def test_dp_epsilon_bounds():
    text = (PRIV / "differential-privacy.md").read_text()
    assert "1.0" in text
    assert "10" in text

def test_dsr_times():
    text = (PRIV / "dsr.md").read_text()
    assert "30 days" in text
