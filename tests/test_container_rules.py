"""Verify container security rules and examples."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

def test_container_rules_present():
    for name in ["docker.md", "image-signing.md", "runtime-security.md"]:
        assert (ROOT / "rules" / "containers" / name).exists()

def test_dockerfile_non_root():
    text = (ROOT / "examples" / "secure" / "docker" / "Dockerfile").read_text()
    assert "USER 10001:10001" in text
    assert "FROM gcr.io/distroless" in text
    assert "latest" not in text

def test_compose_read_only():
    text = (ROOT / "examples" / "secure" / "docker" / "docker-compose.yml").read_text()
    assert "read_only: true" in text
    assert "cap_drop:" in text
    assert "no-new-privileges:true" in text

def test_seccomp_blocks_dangerous():
    import json
    data = json.loads((ROOT / "examples" / "secure" / "docker" / "seccomp.json").read_text())
    blocked = data["syscalls"][1]["names"]
    for name in ["ptrace", "mount", "bpf"]:
        assert name in blocked
