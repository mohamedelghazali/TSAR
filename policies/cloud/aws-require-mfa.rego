package cloud.aws_require_mfa

import rego.v1

violation contains {"msg": msg, "resource": resource.address} if {
  resource := input.resource_changes[_]
  resource.type == "aws_iam_policy"
  policy := json.unmarshal(resource.change.after.policy)
  statement := policy.Statement[_]
  statement.Effect == "Allow"
  statement.Action[_] == "*"
  statement.Resource[_] == "*"
  not has_mfa_condition(statement)
  msg := sprintf("IAM policy %v allows * without MFA condition", [resource.address])
}

has_mfa_condition(statement) if {
  statement.Condition.Bool["aws:MultiFactorAuthPresent"] == "true"
}
