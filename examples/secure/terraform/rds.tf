resource "aws_db_instance" "app" {
  identifier                          = "tsar-app-${var.environment}"
  engine                              = "postgres"
  engine_version                      = "16.2"
  instance_class                      = "db.t4g.medium"
  allocated_storage                   = 100
  storage_encrypted                   = true
  kms_key_id                          = aws_kms_key.app.arn
  storage_type                        = "gp3"
  db_subnet_group_name                = aws_db_subnet_group.app.name
  parameter_group_name                = aws_db_parameter_group.app.name
  username                            = "tsaradmin"
  manage_master_user_password         = true
  vpc_security_group_ids              = [aws_security_group.rds.id]
  publicly_accessible                 = false
  multi_az                            = var.environment == "prod"
  backup_retention_period             = 30
  backup_window                       = "03:00-04:00"
  maintenance_window                  = "sun:04:00-sun:05:00"
  deletion_protection                 = var.environment == "prod"
  copy_tags_to_snapshot               = true
  auto_minor_version_upgrade          = true
  enabled_cloudwatch_logs_exports     = ["postgresql"]
  performance_insights_enabled        = true
  performance_insights_kms_key_id     = aws_kms_key.app.arn
  iam_database_authentication_enabled = true

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_db_parameter_group" "app" {
  name                                = "tsar-app-${var.environment}"
  family                              = "postgres16"
  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }
  parameter {
    name  = "log_connections"
    value = "1"
  }
  parameter {
    name  = "log_disconnections"
    value = "1"
  }
}
