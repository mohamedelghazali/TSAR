# Kubernetes Example Deployment Prerequisites

These manifests are a hardened deployment template, not a ready-to-apply release bundle. Replace every explicitly marked deployment input before applying them.

## Required inputs

1. **Application image:** Replace the image reference in `deployment.yaml` with an image that you have built, scanned, published, and verified. Use an immutable SHA-256 digest, not a mutable tag. The application must:
   - listen with TLS on port `8443`;
   - expose HTTPS health endpoints `/healthz` and `/ready`;
   - run as UID/GID `10001`;
   - support a read-only root filesystem and write only to the mounted `/tmp` volume;
   - read `DATABASE_URL` and `JWT_SECRET` from the injected environment.

2. **IRSA role:** Replace the marked account ID in `serviceaccount.yaml` with the AWS account ID and role name created for this workload. The role trust policy must bind the cluster OIDC provider to `system:serviceaccount:tsar-example:tsar-app`.

3. **External Secrets Operator:** Install and configure the operator and a `ClusterSecretStore` named `aws-secrets-manager` before applying `secret.yaml`. Grant the operator access only to the required Secrets Manager entries.

4. **AWS Secrets Manager entries:** Provision these values outside Git:
   - `tsar/app/database_url`
   - `tsar/app/jwt_secret`
   - `tsar/app/tls_crt`
   - `tsar/app/tls_key`

   The TLS entries must contain a certificate and its matching private key. The ExternalSecret creates the Kubernetes TLS Secret `tsar-app-tls`; no certificate or private key is stored in this repository.

5. **Cluster networking:** Provide an ingress controller in namespace `ingress-nginx`, DNS access, and the required database route. Review the NetworkPolicy selectors and destination ranges against the actual cluster before deployment.

## Validation and deployment

Run schema validation with the repository's Infrastructure Validation workflow. The ExternalSecret CRD schema is pinned to a specific CRDs-catalog commit. Schema validation does not prove that the operator, AWS credentials, referenced secrets, image, certificate, IAM role, or network routes exist.

Do not apply these manifests until all marked values and external prerequisites have been provisioned and reviewed. No live cluster deployment is performed by this repository validation.
