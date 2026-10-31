resource "aws_security_group" "app" {
  name        = "tsar-app-${var.environment}"
  description = "Application workload security group"
  vpc_id      = aws_vpc.main.id

  tags = { Name = "tsar-app-${var.environment}" }
}

resource "aws_security_group" "rds" {
  name        = "tsar-rds-${var.environment}"
  description = "RDS access from application workloads only"
  vpc_id      = aws_vpc.main.id

  tags = { Name = "tsar-rds-${var.environment}" }
}

# Separate rule resources avoid a dependency cycle between the two security groups.
resource "aws_vpc_security_group_egress_rule" "app_to_rds" {
  security_group_id            = aws_security_group.app.id
  referenced_security_group_id = aws_security_group.rds.id
  description                  = "Postgres traffic from app workloads to RDS only"
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
}

resource "aws_vpc_security_group_ingress_rule" "rds_from_app" {
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = aws_security_group.app.id
  description                  = "Postgres traffic from application workloads only"
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
}
