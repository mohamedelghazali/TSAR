variable "aws_region" {
  type        = string
  description = "AWS region for the WORM service."
}

variable "bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name. COMPLIANCE retention is irreversible for retained versions."
}

variable "table_name" {
  type    = string
  default = "tsar-worm-anchors"
}

variable "name_prefix" {
  type    = string
  default = "tsar"
}

variable "service_id" {
  type    = string
  default = "tsar-worm-service"
}

variable "retention_days" {
  type    = number
  default = 365
  validation {
    condition     = var.retention_days >= 1 && var.retention_days <= 36500 && floor(var.retention_days) == var.retention_days
    error_message = "retention_days must be between 1 and 36500."
  }
}

variable "token_secret_arn" {
  type        = string
  sensitive   = true
  description = "Secrets Manager ARN containing the bearer token as SecretString."
}

variable "allowed_repositories" {
  type    = list(string)
  default = ["mohamedelghazali/TSAR"]
}
