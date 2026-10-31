resource "aws_backup_vault" "tsar" {
  name        = "tsar-vault"
  kms_key_arn = aws_kms_key.backup.arn

  # WORM enforced at the vault level.
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_backup_vault_lock_configuration" "tsar" {
  backup_vault_name   = aws_backup_vault.tsar.name
  changeable_for_days = 3
  min_retention_days  = 365
  max_retention_days  = 3650
}

resource "aws_backup_plan" "tsar" {
  name = "tsar-daily"

  rule {
    rule_name         = "daily"
    target_vault_name = aws_backup_vault.tsar.name
    schedule          = "cron(0 2 * * ? *)"
    start_window      = 60
    completion_window = 180

    lifecycle {
      delete_after = 30
    }

    copy_action {
      destination_vault_arn = aws_backup_vault.tsar_cross_region.arn
      lifecycle {
        delete_after = 365
      }
    }

    recovery_point_tags = {
      Retention = "compliance"
      Owner     = "security"
    }
  }

  rule {
    rule_name         = "monthly"
    target_vault_name = aws_backup_vault.tsar.name
    schedule          = "cron(0 3 1 * ? *)"
    lifecycle {
      cold_storage_after = 30
      delete_after       = 3650
    }
  }
}

resource "aws_backup_vault" "tsar_cross_region" {
  provider    = aws.dr_region
  name        = "tsar-vault-dr"
  kms_key_arn = aws_kms_key.backup_dr.arn

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_backup_vault_lock_configuration" "tsar_cross_region" {
  provider            = aws.dr_region
  backup_vault_name   = aws_backup_vault.tsar_cross_region.name
  changeable_for_days = 3
  min_retention_days  = 365
  max_retention_days  = 3650
}

resource "aws_backup_selection" "tsar" {
  name         = "tsar-selection"
  plan_id      = aws_backup_plan.tsar.id
  iam_role_arn = aws_iam_role.backup.arn

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = "true"
  }
}

data "aws_iam_policy_document" "backup_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["backup.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "backup" {
  name               = "tsar-backup-role"
  assume_role_policy = data.aws_iam_policy_document.backup_assume.json
}

resource "aws_iam_role_policy_attachment" "backup" {
  role       = aws_iam_role.backup.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}