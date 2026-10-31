package cloud.aws_require_mfa

violation[{"msg": msg, "resource": input.resource.address}] {
  resource := input.resource_changes[_]
  resource.type == "aws_iam_policy"
  statement := json.unmarshal(resource.change.after.policy).Statement[_]
  statement.Effect == "Allow"
  statement.Action[_] == "*"
  statement.Resource[_] == "*"
  not has_mfa_condition(statement)
  msg := sprintf("IAM policy %v allows * without MFA condition", [resource.address])
}

has_mfa_condition(statement) {
  statement.Condition.Bool["aws:MultiFactorAuthPresent"] == "true"
}
