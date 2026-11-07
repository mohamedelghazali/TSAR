output "api_endpoint" {
  value       = aws_apigatewayv2_api.anchor.api_endpoint
  description = "HTTPS endpoint to configure in TSAR."
}

output "service_id" {
  value = var.service_id
}

output "signing_key_arn" {
  value       = aws_kms_key.signing.arn
  description = "Export its public key and pin it out-of-band in the TSAR service trust file."
}

output "anchor_bucket_name" {
  value = aws_s3_bucket.anchors.bucket
}

output "anchor_table_name" {
  value = aws_dynamodb_table.anchors.name
}
