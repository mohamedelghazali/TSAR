# GCP Security Baseline

## Identity
- Workforce Identity Federation for humans; no long-lived service account keys.
- Service accounts: per-workload, least privilege, no `roles/owner` in production.
- Organization policies to restrict resource locations and disable default SA key creation.

## Networking
- VPC with Private Google Access; no external IPs on compute.
- Firewall rules: deny by default; explicit allow with target tags.
- VPC Service Controls perimeters around sensitive services.
- Cloud NAT for egress.

## Compute
- GCE: Shielded VMs (vTPM, integrity monitoring, secure boot).
- GKE: Workload Identity, Binary Authorization, private cluster, shielded nodes.
- Cloud Run: ingress restricted, no unauthenticated access unless intended.

## Storage
- GCS: Uniform bucket-level access, public access prevention, CMEK for sensitive data.
- BigQuery: CMEK, column-level access control, row-level security.
- Persistent disks: encrypted (default), CMEK for sensitive.

## Logging
- Cloud Audit Logs: Admin, Data Read, Data Write for sensitive services.
- Log sink to a dedicated project with restricted access.
- Security Command Center Premium enabled.

## KMS
- CMEK with per-workload key rings.
- Rotation period <= 90 days for symmetric keys.
- IAM roles scoped to key, not project.

## Secrets
- Secret Manager with rotation and audit logging.
- Never in environment variables or ConfigMaps for sensitive values.

## Forbidden
- Service account keys stored in code.
- Public GCS buckets.
- `roles/editor` on production projects.
- Default VPC in production.
