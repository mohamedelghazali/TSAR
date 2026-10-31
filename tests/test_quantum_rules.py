"""Verify PQC rules reference required algorithms and parameters."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def test_ml_kem_mentions_768():
    text = (ROOT / "rules" / "quantum" / "ml-kem.md").read_text()
    assert "ML-KEM-768" in text
    assert "ML-KEM-1024" in text

def test_ml_dsa_mentions_44_and_87():
    text = (ROOT / "rules" / "quantum" / "ml-dsa.md").read_text()
    assert "ML-DSA-44" in text
    assert "ML-DSA-87" in text

def test_slh_dsa_variants():
    text = (ROOT / "rules" / "quantum" / "slh-dsa.md").read_text()
    for v in ["128s", "192s", "256s"]:
        assert v in text

def test_hybrid_rules_forbid_xor():
    text = (ROOT / "rules" / "quantum" / "hybrid-design.md").read_text()
    assert "XOR" in text
    assert "concatenate" in text.lower()
