package terraform.require_encryption

import rego.v1

violation contains {"msg": msg, "resource": resource.address} if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket"
  not has_encryption(resource)
  msg := sprintf("S3 bucket %v must have encryption configured", [resource.address])
}

has_encryption(resource) if {
  object.get(resource.change.after, "server_side_encryption_configuration", null) != null
} else if {
  some child in input.resource_changes
  child.type == "aws_s3_bucket_server_side_encryption_configuration"
  child.change.after.bucket == resource.change.after.bucket
}
