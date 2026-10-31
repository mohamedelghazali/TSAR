data "aws_iam_policy_document" "app_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:tsar-example:tsar-app"]
    }
  }
}

resource "aws_iam_role" "app" {
  name                 = "tsar-app-${var.environment}"
  assume_role_policy   = data.aws_iam_policy_document.app_assume.json
  max_session_duration = 3600
}

data "aws_iam_policy_document" "app" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = ["${aws_s3_bucket.app.arn}/*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey",
    ]
    resources = [aws_kms_key.app.arn]
  }
}

resource "aws_iam_role_policy" "app" {
  role   = aws_iam_role.app.id
  name   = "tsar-app"
  policy = data.aws_iam_policy_document.app.json
}
