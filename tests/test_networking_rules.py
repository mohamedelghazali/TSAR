from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NET = ROOT / "rules" / "networking"

def test_files_present():
    for name in ["dns.md", "mtls.md", "service-mesh.md", "waf.md",
                 "zero-trust.md", "load-balancer.md"]:
        assert (NET / name).exists()

def test_dns_requires_dnssec():
    text = (NET / "dns.md").read_text()
    assert "DNSSEC" in text
    assert "CAA" in text

def test_mtls_forbids_long_lived():
    text = (NET / "mtls.md").read_text()
    assert "24 hours" in text
    assert "InsecureSkipVerify" in text

def test_zero_trust_principles():
    text = (NET / "zero-trust.md").read_text()
    assert "Never trust" in text
    assert "micro-segmentation" in text.lower() or "Micro-segmentation" in text
