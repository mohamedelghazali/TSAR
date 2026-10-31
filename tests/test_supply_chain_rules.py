"""Verify supply chain rules cover required artifacts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SC = ROOT / "rules" / "supply-chain"

def test_files_present():
    for name in ["sbom-slsa.md", "dependency-integrity.md", "artifact-signing.md"]:
        assert (SC / name).exists()

def test_sbom_formats():
    text = (SC / "sbom-slsa.md").read_text()
    assert "CycloneDX" in text
    assert "SPDX" in text

def test_artifact_signing_references_sigstore():
    text = (SC / "artifact-signing.md").read_text()
    assert "Sigstore" in text
    assert "Rekor" in text
