# Policy as Code

## Tools
- Open Policy Agent (OPA/Rego), Cedar, Kyverno, Conftest.
- Enforce in CI, admission controllers, and runtime.

## Policy Categories
- **Preventive**: block non-compliant resources (Kyverno, admission).
- **Detective**: alert on violations (OPA, cloud config rules).
- **Corrective**: auto-remediate where safe (limited scope).

## Repository Structure
```
policies/
  kubernetes/
    disallow-privileged.rego
    require-non-root.rego
  terraform/
    require-encryption.rego
    require-tags.rego
  cloud/
    aws-require-mfa.rego
```

## Testing
- Unit tests for each policy.
- Positive and negative test cases.
- Integration tests against sample resources.

## Rollout
1. Detect-only mode for 2 weeks.
2. Review alerts; tune policies.
3. Enforce mode.
4. Document exceptions with expiry.

## Forbidden
- Wildcard exceptions.
- Policies without tests.
- Silent policy failures.
