output "app_role_arn" {
  value       = aws_iam_role.app.arn
  description = "IAM role ARN for the app"
}

output "kms_key_arn" {
  value       = aws_kms_key.app.arn
  description = "KMS key ARN for data encryption"
  sensitive   = false
}

output "db_endpoint" {
  value       = aws_db_instance.app.endpoint
  description = "RDS endpoint"
  sensitive   = true
}
