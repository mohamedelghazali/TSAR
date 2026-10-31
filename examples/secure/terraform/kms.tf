resource "aws_kms_key" "app" {
  description             = "TSAR app encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnableRootAccountAdmin"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      },
      {
        Sid       = "AllowAppUse"
        Effect    = "Allow"
        Principal = { AWS = aws_iam_role.app.arn }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey",
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "s3.${var.region}.amazonaws.com"
          }
        }
      },
    ]
  })
}

resource "aws_kms_alias" "app" {
  name          = "alias/tsar-app-${var.environment}"
  target_key_id = aws_kms_key.app.key_id
}
