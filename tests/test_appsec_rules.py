from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "rules" / "application-security"

def test_files_present():
    for name in ["spa.md", "csp.md", "mobile-app.md", "desktop-app.md"]:
        assert (APP / name).exists()

def test_spa_forbids_localstorage():
    text = (APP / "spa.md").read_text()
    assert "localStorage" in text
    assert "HttpOnly" in text

def test_csp_forbids_wildcard():
    text = (APP / "csp.md").read_text()
    assert "default-src *" in text or "Forbidden" in text
