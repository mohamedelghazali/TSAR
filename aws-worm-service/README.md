# TSAR AWS WORM Anchor Service

This directory contains an AWS Lambda implementation of the external anchor API
and Terraform for a deployment that has not been provisioned by this repository.

## Architecture

- API Gateway HTTP API exposes the two endpoints used by \`tools/tsar-cli/lifecycle_anchor.py\`.
- Lambda validates the bearer token from AWS Secrets Manager, request shape, repository allowlist, run identity, audit snapshot bytes/digest, idempotency key, and expected previous receipt digest.
- DynamoDB stores run state, append records, and idempotency records. A single \`TransactWriteItems\` operation commits the anchor, idempotency record, and sequence/state transition atomically.
- S3 Object Lock stores the complete Base64-carried audit snapshot, referenced evidence files, request, and signed receipt in a versioned bucket with explicit COMPLIANCE retention. The service checks the supplied bytes against `record_sha256` and recomputes the stable run ID before archiving. The service checks the retention mode and expiry returned by S3 before committing the DynamoDB index.
- AWS KMS uses an asymmetric Ed25519 key (\`ECC_NIST_EDWARDS25519\`) to sign the canonical receipt. The private key is never exported.

## Consistency and failure behavior

S3 and DynamoDB do not share a distributed transaction. The service therefore writes and verifies the immutable S3 object first, then commits the authoritative index and sequence in a DynamoDB transaction. If the transaction fails, the S3 version can remain as a retained orphan. It is not returned by the API and is not considered an accepted anchor. A caller must fetch the latest receipt and retry. Concurrent append attempts are serialized by conditional transactional state updates.

The idempotency record is committed in the same DynamoDB transaction as the anchor. A repeated idempotency key with different content is rejected. DynamoDB's transaction client token is an additional short-lived retry safeguard, not the long-term idempotency mechanism.

## Prerequisites

- An AWS account and deployment identity with permission to create the resources in \`terraform/main.tf\`.
- Terraform 1.6 or later and the AWS provider 6.x.
- A pre-created Secrets Manager secret whose \`SecretString\` is the bearer token. Do not put the token in Terraform variables, state, shell history, source control, or command-line arguments.
- A globally unique S3 bucket name.
- An explicit retention decision. The example defaults to 365 days. S3 COMPLIANCE retention cannot be shortened or bypassed for retained object versions, including by the account root user.

## Build and deploy (operator-controlled; not run by CI)

From this directory:

1. Create a random bearer token and store it in Secrets Manager. Record only the secret ARN.
2. Review and set \`aws_region\`, \`bucket_name\`, \`token_secret_arn\`, \`retention_days\`, and \`allowed_repositories\` in a private tfvars file. Never commit that file.
3. Run \`terraform init\`, \`terraform fmt -check\`, \`terraform validate\`, and \`terraform plan\`. Review the plan carefully before any apply.
4. Only after explicit operational approval, run \`terraform apply\`.
5. Retrieve the KMS public key using \`GetPublicKey\`. Confirm its key spec is \`ECC_NIST_EDWARDS25519\`, serialize the raw 32-byte Ed25519 public key, and place its Base64 value in an external \`tsar/audit-anchor-trust/v1\` trust file. Distribute and pin that trust file through an independent administrative channel.
6. Set \`TSAR_AUDIT_ANCHOR_TOKEN\` in the TSAR runtime environment and use the API endpoint output with \`tsar lifecycle-anchor\`.

The KMS \`Sign\` call uses \`ED25519_SHA_512\` with \`MessageType=RAW\`, matching the standard Ed25519 signature verified by the TSAR client. Do not switch to the pre-hash variant without changing and testing the client protocol.

## Security boundaries and remaining production work

- CI only performs static validation. It does not create AWS resources, access credentials, or prove that a deployed account has the intended controls.
- The API bearer token is a shared credential. Rotate it through Secrets Manager and keep it separate from the KMS signing key. Consider adding a dedicated authorizer/WAF and per-client credentials before multi-tenant use.
- The Lambda execution role cannot delete S3 objects or versions. S3 COMPLIANCE retention protects retained versions against deletion during the retention period, but it does not prevent account compromise, policy mistakes before upload, or deletion after retention expires.
- DynamoDB is the live index and sequencing authority; S3 Object Lock is the immutable evidence archive. Protect the table, backups, Terraform state, deployment role, and CloudTrail separately.
- Monitor Object Lock configuration, bucket policy, KMS key state, Secrets Manager rotation, Lambda errors, API throttling, and DynamoDB transaction conflicts.
- The service currently permits only configured repository names. Review this allowlist before onboarding another repository.
- The combined decoded audit snapshot and evidence archive is limited to 4 MiB to remain within synchronous Lambda invocation payload constraints.
- The S3 object and DynamoDB transaction cannot be atomic together. Retained orphan objects after failed transactions are expected and must be monitored/reconciled, never treated as accepted anchors.
- This implementation is a deployment candidate, not a claim of operational WORM protection. No AWS resources have been deployed or independently audited by this repository change.

## API compatibility

- \`GET /v1/runs/{run_id}/latest\`: HTTP 200 with \`{"receipt": ...}\`, or HTTP 404 when no accepted anchor exists.
- \`POST /v1/anchors\`: HTTP 201 with \`{"receipt": ...}\` after S3 retention verification and DynamoDB transaction commit.
- Receipts use \`tsar/external-audit-anchor-receipt/v1\`; the Ed25519 signature covers every field except \`signature\`.
- The service returns HTTP 409 for stale sequence/concurrent append conflicts. The client should fetch the latest receipt and retry.
