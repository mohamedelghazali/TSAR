# Vendored Kubernetes schemas

- \`external-secrets.io/externalsecret_v1beta1.json\` is copied from
  \`datreeio/CRDs-catalog\` at commit
  \`3eb90d47aba8d61919d4419dd38301536e32a94b\`.
- The source file is
  \`external-secrets.io/externalsecret_v1beta1.json\`.
- Update this schema only alongside a reviewed External Secrets Operator API
  version change. Do not fetch an unpinned \`main\` or \`master\` schema during CI.

This schema validates the ExternalSecret manifest shape; it does not prove that
the External Secrets Operator, ClusterSecretStore, AWS identity, or remote
secrets exist in a target cluster.
