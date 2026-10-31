# CI/CD Integration

TSAR ships four ready-made pipeline templates. All run the same three checks:

1. **Secret scan** — blocks on any hardcoded secret.
2. **Secure review** — blocks on HIGH findings.
3. **Crypto inventory** — reports CBOM, flags weak algorithms.

## GitHub Actions
Copy `integrations/github-actions/tsar.yml` to `.github/workflows/tsar.yml`.

The workflow runs on every push and pull request. It fails on secret or HIGH findings.

## GitLab CI
Copy `integrations/gitlab-ci/tsar.yml` to `.gitlab-ci.yml` (or include it).

The job `tsar:scan` runs in the `test` stage and blocks the pipeline on failure.

## Bitbucket Pipelines
Copy `integrations/bitbucket/tsar.yml` to `bitbucket-pipelines.yml`.

The `tsar-scan` step runs on every branch.

## Azure DevOps
Copy `integrations/azure-devops/tsar.yml` as a pipeline template and reference it from your main pipeline.

## Fail-Closed Policy
All integrations fail the pipeline on any HIGH finding or any secret detection. Do not allow override without a documented exception approved by security.

## Reporting
The `crypto-inventory` step writes `cbom.json` as an artifact. Retain per release for audit.
