"""Verify cloud rule files exist and contain required controls."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CLOUD = ROOT / "rules" / "cloud"

REQUIRED = {
    "aws.md": ["IMDSv2", "S3", "KMS", "CloudTrail", "GuardDuty"],
    "gcp.md": ["VPC Service Controls", "Binary Authorization", "CMEK", "Workload Identity"],
    "azure.md": ["Managed Identities", "PIM", "Key Vault", "Defender"],
    "multi-cloud.md": ["Federation", "SIEM"],
}

def test_cloud_files_exist():
    for name in REQUIRED:
        assert (CLOUD / name).exists(), f"missing {name}"

def test_cloud_controls_present():
    for name, controls in REQUIRED.items():
        text = (CLOUD / name).read_text()
        for c in controls:
            assert c in text, f"{name} missing control: {c}"
