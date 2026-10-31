from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEV = ROOT / "rules" / "development"

def test_files_present():
    for name in ["secure-sdlc.md", "code-review.md",
                 "pair-programming.md", "dependency-review.md"]:
        assert (DEV / name).exists()

def test_sdlc_has_gates():
    text = (DEV / "secure-sdlc.md").read_text()
    assert "Design gate" in text
    assert "Release gate" in text

def test_dependency_review_has_sla():
    text = (DEV / "dependency-review.md").read_text()
    assert "Critical: 24" in text or "24 hours" in text
