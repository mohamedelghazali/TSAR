output "api_endpoint" { value = aws_apigatewayv2_api.anchor.api_endpoint }
output "service_id" { value = var.service_id }
output "signing_key_arn" { value = aws_kms_key.signing.arn }
output "anchor_bucket_name" { value = aws_s3_bucket.anchors.bucket }
output "anchor_table_name" { value = aws_dynamodb_table.anchors.name }
