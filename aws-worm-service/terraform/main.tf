terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

resource "aws_s3_bucket" "anchors" {
  bucket              = var.bucket_name
  object_lock_enabled = true
  force_destroy       = false
  tags = {
    Project = "TSAR"
    Purpose = "Immutable lifecycle audit evidence"
  }
}

resource "aws_s3_bucket_versioning" "anchors" {
  bucket = aws_s3_bucket.anchors.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_object_lock_configuration" "anchors" {
  bucket = aws_s3_bucket.anchors.id
  rule {
    default_retention {
      mode = "COMPLIANCE"
      days = var.retention_days
    }
  }
  depends_on = [aws_s3_bucket_versioning.anchors]
}

resource "aws_s3_bucket_server_side_encryption_configuration" "anchors" {
  bucket = aws_s3_bucket.anchors.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "anchors" {
  bucket                  = aws_s3_bucket.anchors.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "anchors" {
  bucket = aws_s3_bucket.anchors.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [aws_s3_bucket.anchors.arn, "${aws_s3_bucket.anchors.arn}/*"]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
      {
        Sid       = "DenyNonComplianceObjectWrites"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.anchors.arn}/*"
        Condition = {
          StringNotEquals = {
            "s3:object-lock-mode" = "COMPLIANCE"
          }
        }
      },
      {
        Sid       = "DenyShortRetention"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.anchors.arn}/*"
        Condition = {
          NumericLessThan = {
            "s3:object-lock-remaining-retention-days" = var.retention_days
          }
        }
      }
    ]
  })
}

resource "aws_dynamodb_table" "anchors" {
  name                        = var.table_name
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "pk"
  range_key                   = "sk"
  deletion_protection_enabled = true

  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "sk"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
  server_side_encryption {
    enabled = true
  }
  tags = {
    Project = "TSAR"
    Purpose = "Anchor ordering and idempotency"
  }
}

resource "aws_kms_key" "signing" {
  description              = "TSAR external WORM receipt Ed25519 signing key"
  key_usage                = "SIGN_VERIFY"
  customer_master_key_spec = "ECC_NIST_EDWARDS25519"
  deletion_window_in_days  = 30
  enable_key_rotation      = false
  tags = {
    Project = "TSAR"
    Purpose = "WORM receipt signing"
  }
}

resource "aws_kms_alias" "signing" {
  name          = "alias/tsar-worm-receipt-signing"
  target_key_id = aws_kms_key.signing.key_id
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.name_prefix}-worm-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy" "lambda" {
  name = "${var.name_prefix}-worm-runtime"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:PutObjectRetention", "s3:GetObjectRetention"]
        Resource = "${aws_s3_bucket.anchors.arn}/runs/*"
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:GetItem", "dynamodb:TransactWriteItems"]
        Resource = aws_dynamodb_table.anchors.arn
      },
      {
        Effect   = "Allow"
        Action   = ["kms:Sign"]
        Resource = aws_kms_key.signing.arn
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = var.token_secret_arn
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:${data.aws_partition.current.partition}:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.name_prefix}-worm-anchor"
  retention_in_days = 90
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../lambda/handler.py"
  output_path = "${path.module}/worm-anchor.zip"
}

resource "aws_lambda_function" "anchor" {
  function_name    = "${var.name_prefix}-worm-anchor"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      ANCHOR_BUCKET        = aws_s3_bucket.anchors.bucket
      ANCHOR_TABLE         = aws_dynamodb_table.anchors.name
      SIGNING_KEY_ARN      = aws_kms_key.signing.arn
      TOKEN_SECRET_ARN     = var.token_secret_arn
      SERVICE_ID           = var.service_id
      RETENTION_DAYS       = tostring(var.retention_days)
      ALLOWED_REPOSITORIES = join(",", var.allowed_repositories)
    }
  }
  depends_on = [aws_cloudwatch_log_group.lambda, aws_iam_role_policy.lambda]
}

resource "aws_apigatewayv2_api" "anchor" {
  name          = "${var.name_prefix}-worm-anchor"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "anchor" {
  api_id                 = aws_apigatewayv2_api.anchor.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.anchor.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "append" {
  api_id    = aws_apigatewayv2_api.anchor.id
  route_key = "POST /v1/anchors"
  target    = "integrations/${aws_apigatewayv2_integration.anchor.id}"
}

resource "aws_apigatewayv2_route" "latest" {
  api_id    = aws_apigatewayv2_api.anchor.id
  route_key = "GET /v1/runs/{run_id}/latest"
  target    = "integrations/${aws_apigatewayv2_integration.anchor.id}"
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/apigateway/${var.name_prefix}-worm-anchor"
  retention_in_days = 90
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.anchor.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 20
    throttling_rate_limit  = 10
    detailed_metrics_enabled = true
  }

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api.arn
    format = jsonencode({
      requestId = "$context.requestId"
      sourceIp  = "$context.identity.sourceIp"
      requestTime = "$context.requestTime"
      httpMethod = "$context.httpMethod"
      routeKey = "$context.routeKey"
      status = "$context.status"
      protocol = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }
}

resource "aws_lambda_permission" "api" {
  statement_id  = "AllowHttpApiInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.anchor.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.anchor.execution_arn}/*/*"
}
