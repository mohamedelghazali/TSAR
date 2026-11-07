# TSAR AWS WORM Anchor Service

This directory contains an AWS Lambda implementation of the external anchor API
and Terraform for a deployment that has not been provisioned by this repository.

## Architecture

- API Gateway HTTP API exposes the two endpoints used by `tools/tsar-cli/lifecycle_anchor.py`.
- Lambda validates the bearer token from AWS Secrets Manager, request shape, repository allowlist, run identity, audit snapshot bytes/digest, idempotency key, and expected previous receipt digest.
- DynamoDB stores run state, append records, and idempotency records. A single `TransactWriteItems` operation commits the anchor, idempotency record, and sequence/state transition atomically.
- S3 Object Lock stores the complete Base64-carried audit snapshot, referenced evidence files, request, and signed receipt in a versioned bucket with explicit COMPLIANCE retention. The service checks the supplied bytes against `record_sha256` and recomputes the stable run ID before archiving. The service checks the retention mode and expiry returned by S3 before committing the DynamoDB index.
- AWS KMS uses an asymmetric Ed25519 key (`ECC_NIST_EDWARDS25519`) to sign the canonical receipt. The private key is never exported.

## Consistency and failure behavior

S3 and DynamoDB do not share a distributed transaction. The service therefore writes and verifies the immutable S3 object first, then commits the authoritative index and sequence in a DynamoDB transaction. If the transaction fails, the S3 version can remain as a retained orphan. It is not returned by the API and is not considered an accepted anchor. A caller must fetch the latest receipt and retry. Concurrent append attempts are serialized by conditional transactional state updates.

The idempotency record is committed in the same DynamoDB transaction as the anchor. A repeated idempotency key with different content is rejected. DynamoDB's transaction client token is an additional short-lived retry safeguard, not the long-term idempotency mechanism.

## Prerequisites

- An AWS account and deployment identity with permission to create the resources in `terraform/main.tf`.
- Terraform 1.6 or later and the AWS provider 6.x.
- A pre-created Secrets Manager secret whose `SecretString` is the bearer token. Do not put the token in Terraform variables, state, shell history, source control, or command-line arguments.
- A globally unique S3 bucket name.
- An explicit retention decision. The example defaults to 365 days. S3 COMPLIANCE retention cannot be shortened or bypassed for retained object versions, including by the account root user.

## Deploy and live-test from GitHub Actions

Use the manually dispatched workflow
`.github/workflows/aws-worm-deploy.yml`. It uses GitHub OIDC and stores no
long-lived AWS access key.

### One-time AWS/GitHub setup

1. Enable the GitHub Actions OIDC provider
   `token.actions.githubusercontent.com` in the target AWS account.
2. Create a dedicated deployment role trusted only for subject
   `repo:mohamedelghazali/TSAR:environment:aws-production` and audience
   `sts.amazonaws.com`. Scope it to the Terraform state bucket, resources in
   this service, read access to the configured Secrets Manager secret, and
   `iam:PassRole` only for the Lambda execution role.
3. Create the GitHub environment `aws-production` and configure required
   reviewers as the production deployment gate.
4. Create a Secrets Manager secret whose `SecretString` is a high-entropy
   bearer token. Never place it in GitHub inputs, source, Terraform variables,
   or logs.
5. Choose two different globally unique buckets: Terraform state and immutable
   evidence archive.

### Dispatch

Open **Actions → AWS WORM Deploy and Live Qualification → Run workflow**.
Provide the role ARN, region, both bucket names, secret ARN, and retention.

- `plan-only` validates and displays a Terraform plan without provisioning.
- `apply` bootstraps an encrypted/versioned state bucket with S3 lockfile
  locking, applies the saved plan, and runs live qualification.
- `apply` requires explicit acknowledgement of irreversible S3 Object Lock
  COMPLIANCE retention.
- Live tests cover unauthenticated rejection, append, KMS Ed25519 signature
  verification, latest-anchor read, idempotent retry, S3 versioning, Object
  Lock COMPLIANCE mode, and public-access blocking.

The workflow does not run on pull requests, stores no AWS credentials, and
does not destroy resources or shorten retention. Existing state-bucket policies
are preserved; an existing bucket must already deny insecure transport.

The KMS `Sign` call uses `ED25519_SHA_512` with `MessageType=RAW`, matching the standard Ed25519 signature verified by the TSAR client. Do not switch to the pre-hash variant without changing and testing the client protocol.

## Security boundaries and remaining production work

- Ordinary pull-request and push CI performs static validation only. The dedicated GitHub Actions workflow can provision AWS only when manually dispatched in apply mode with an OIDC deployment role, a configured production environment, and the explicit retention acknowledgement.
- The API bearer token is a shared credential. Rotate it through Secrets Manager and keep it separate from the KMS signing key. Consider adding a dedicated authorizer/WAF and per-client credentials before multi-tenant use.
- The Lambda execution role cannot delete S3 objects or versions. S3 COMPLIANCE retention protects retained versions against deletion during the retention period, but it does not prevent account compromise, policy mistakes before upload, or deletion after retention expires.
- DynamoDB is the live index and sequencing authority; S3 Object Lock is the immutable evidence archive. Protect the table, backups, Terraform state, deployment role, and CloudTrail separately.
- Monitor Object Lock configuration, bucket policy, KMS key state, Secrets Manager rotation, Lambda errors, API throttling, and DynamoDB transaction conflicts.
- The service currently permits only configured repository names. Review this allowlist before onboarding another repository.
- The combined decoded audit snapshot and evidence archive is limited to 4 MiB to remain within synchronous Lambda invocation payload constraints.
- The S3 object and DynamoDB transaction cannot be atomic together. Retained orphan objects after failed transactions are expected and must be monitored/reconciled, never treated as accepted anchors.
- The implementation and workflow do not themselves establish operational WORM protection. Only a successful GitHub Actions apply followed by the authenticated live qualification and deployed-control checks can establish the recorded operational state; green PR CI alone is not deployment evidence.

## API compatibility

- `GET /v1/runs/{run_id}/latest`: HTTP 200 with `{"receipt": ...}`, or HTTP 404 when no accepted anchor exists.
- `POST /v1/anchors`: HTTP 201 with `{"receipt": ...}` after S3 retention verification and DynamoDB transaction commit.
- Receipts use `tsar/external-audit-anchor-receipt/v1`; the Ed25519 signature covers every field except `signature`.
- The service returns HTTP 409 for stale sequence/concurrent append conflicts. The client should fetch the latest receipt and retry.
