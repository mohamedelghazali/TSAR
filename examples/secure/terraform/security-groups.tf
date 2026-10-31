resource "aws_security_group" "app" {
  name        = "tsar-app-${var.environment}"
  description = "Application workload security group"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "Database traffic only"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.private_subnet_cidrs
  }

  tags = { Name = "tsar-app-${var.environment}" }
}

resource "aws_security_group" "rds" {
  name        = "tsar-rds-${var.environment}"
  description = "RDS access from application workloads only"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Postgres from application security group"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = { Name = "tsar-rds-${var.environment}" }
}
