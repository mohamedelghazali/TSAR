from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BK = ROOT / "examples" / "secure" / "backup"

def test_files_present():
    for name in ["restic-backup.sh", "borg-backup.sh", "velero-schedule.yaml",
                 "velero-storage-location.yaml", "aws-backup-vault.tf",
                 "restore-test.sh"]:
        assert (BK / name).exists()

def test_restic_uses_encryption():
    text = (BK / "restic-backup.sh").read_text()
    assert "RESTIC_PASSWORD_FILE" in text
    assert "restic backup" in text
    assert "restic check" in text

def test_velero_uses_object_lock():
    text = (BK / "velero-storage-location.yaml").read_text()
    assert "s3BucketLockEnabled" in text
    assert "COMPLIANCE" in text

def test_aws_backup_vault_lock():
    text = (BK / "aws-backup-vault.tf").read_text()
    assert "aws_backup_vault_lock_configuration" in text
    assert "min_retention_days" in text