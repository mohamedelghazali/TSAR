from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EP = ROOT / "rules" / "endpoint"

def test_files_present():
    for name in ["edr.md", "mdm.md", "disk-encryption.md",
                 "patch-management.md", "application-control.md"]:
        assert (EP / name).exists()

def test_patch_sla_critical():
    text = (EP / "patch-management.md").read_text()
    assert "7 days" in text

def test_disk_encryption_platforms():
    text = (EP / "disk-encryption.md").read_text()
    for p in ["FileVault", "BitLocker", "LUKS", "Data Protection"]:
        assert p in text
