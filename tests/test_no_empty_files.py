"""Prevent empty or trivial files from being committed."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECK_DIRS = ["rules", "prompts", "system", "skills", "docs", "integrations"]
MIN_BYTES = 200
MIN_LINES = 5

def test_no_empty_markdown():
    bad = []
    for d in CHECK_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for f in base.rglob("*.md"):
            if f.stat().st_size < MIN_BYTES:
                bad.append((str(f.relative_to(ROOT)), f"{f.stat().st_size} bytes"))
                continue
            text = f.read_text(errors="ignore")
            if len([l for l in text.splitlines() if l.strip()]) < MIN_LINES:
                bad.append((str(f.relative_to(ROOT)), f"{len(text.splitlines())} lines"))
    assert not bad, "Empty or trivial files:\n" + "\n".join(f"  - {p} ({r})" for p, r in bad)

def test_no_empty_yaml():
    bad = []
    for d in CHECK_DIRS + [".github"]:
        base = ROOT / d
        if not base.exists():
            continue
        for ext in ("*.yml", "*.yaml"):
            for f in base.rglob(ext):
                if f.stat().st_size < MIN_BYTES:
                    bad.append((str(f.relative_to(ROOT)), f"{f.stat().st_size} bytes"))
    assert not bad, "Empty YAML files:\n" + "\n".join(f"  - {p} ({r})" for p, r in bad)
