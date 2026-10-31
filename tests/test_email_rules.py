from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EMAIL = ROOT / "rules" / "email"

def test_files_present():
    for name in ["authentication.md", "secure-gateway.md",
                 "encryption.md", "anti-phishing.md"]:
        assert (EMAIL / name).exists()

def test_dmarc_requires_reject():
    text = (EMAIL / "authentication.md").read_text()
    assert "p=reject" in text

def test_dns_records_have_reject():
    records = (ROOT / "examples" / "secure" / "email" / "dns-records.txt").read_text()
    assert "p=reject" in records
    assert "v=DMARC1" in records
    assert "v=spf1" in records
    assert "-all" in records
