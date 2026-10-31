package terraform.require_encryption

violation[{"msg": msg, "resource": input.resource.address}] {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket"
  not has_encryption(resource)
  msg := sprintf("S3 bucket %v must have encryption configured", [resource.address])
}

has_encryption(resource) {
  some change in resource.change
  change.after.server_side_encryption_configuration
}

has_encryption(resource) {
  some child in input.resource_changes[_]
  child.type == "aws_s3_bucket_server_side_encryption_configuration"
  child.change.after.bucket == resource.change.after.bucket
}
