# Operations Runbook

## Core TSAR release qualification — GitHub-only

The TSAR core release is qualified through GitHub Actions and repository
artifacts. No external cloud account, AWS console work, credential setup,
resource provisioning, or live AWS test is required for the core `1.2.0`
release. Use the repository's CI and release workflows as the authoritative
GitHub-side evidence.

The AWS WORM deployment section below is optional and separate. Do not run it
as part of the core release qualification. Without an actual deployment and
live smoke test, describe the WORM service only as an implementation candidate,
never as operational or production-verified.

## Optional AWS WORM Service — GitHub-dispatched deployment

The AWS WORM anchor service is deployed through the manually dispatched
GitHub Actions workflow
`.github/workflows/aws-worm-deploy.yml`. Ordinary repository CI performs
static validation and isolated tests only; it does not provision AWS.

### One-time prerequisites

1. In the target AWS account, enable the GitHub OIDC provider
   `token.actions.githubusercontent.com`.
2. Create a dedicated deployment IAM role trusted for audience
   `sts.amazonaws.com` and subject
   `repo:mohamedelghazali/TSAR:environment:aws-production`. Restrict its
   permissions to the TSAR WORM resources, Terraform state bucket, one
   Secrets Manager token, and `iam:PassRole` only to the Lambda execution role.
3. Create the GitHub environment `aws-production` and configure required
   reviewers. The deployment workflow uses this environment.
4. Create a high-entropy bearer token in AWS Secrets Manager. Only its ARN is
   entered into the workflow; never expose the token in GitHub inputs, source,
   Terraform variables, or logs.
5. Select two distinct globally unique S3 bucket names: a versioned/encrypted
   Terraform state bucket and the immutable evidence archive.
6. Confirm the target region supports the KMS Ed25519 key type. Decide the
   Object Lock COMPLIANCE retention period and costs before deployment.

### Deploy and qualify

Open **Actions → AWS WORM Deploy and Live Qualification → Run workflow**.

- Run `plan-only` first and inspect the complete Terraform plan.
- For deployment, select `apply` and explicitly acknowledge that S3
  Object Lock COMPLIANCE retention is irreversible for retained object
  versions. The workflow applies the saved plan using Terraform's S3 lockfile
  backend.
- The live test verifies unauthenticated rejection, authenticated append,
  KMS Ed25519 receipt signature, latest-anchor read, idempotent retry, and
  retention metadata. The workflow also verifies S3 versioning, Object Lock
  COMPLIANCE mode, and public-access blocking.
- The workflow exports the public KMS trust file as the
  `tsar-worm-service-trust` Actions artifact. Verify its printed fingerprint
  through an independent administrative channel before distributing it to
  TSAR clients.
- Record the workflow run URL, AWS account/region, resource identifiers,
  retention configuration, test results, and operational owner. Never record
  bearer tokens or other secrets.

Do not claim the service is operational until the apply and every live test
step succeed. Do not run `terraform destroy` against retained evidence or
shorten COMPLIANCE retention. Keep Terraform state access separate from the
Lambda runtime role.

A permanent general-purpose Staging environment is not a TSAR completion
prerequisite. An isolated AWS deployment is sufficient for the live
qualification; it does not imply a permanent Staging environment.
