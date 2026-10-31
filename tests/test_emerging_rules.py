from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EM = ROOT / "rules" / "emerging"

def test_files_present():
    for name in ["advanced-ai-agents.md", "quantum-safe-migration.md",
                 "iomt.md", "autonomous-systems.md"]:
        assert (EM / name).exists()

def test_ai_agents_forbid_wildcard():
    text = (EM / "advanced-ai-agents.md").read_text()
    assert "`*`" in text or "wildcard" in text.lower()
    assert "human approval" in text.lower() or "human confirmation" in text.lower()

def test_quantum_timeline():
    text = (EM / "quantum-safe-migration.md").read_text()
    assert "2035" in text
