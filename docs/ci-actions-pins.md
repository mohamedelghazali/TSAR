# CI Toolchain Pinning

The following GitHub Actions are pinned to immutable commit SHAs rather than moving tags. The referenced source manifests were inspected at the pinned commits on 2026-10-31.

| Action | Pinned source version | Commit SHA |
|---|---:|---|
| actions/checkout | 7.0.1 | \`3d3c42e5aac5ba805825da76410c181273ba90b1\` |
| actions/setup-python | 7.1.0 | \`ec52d0af729a7c50ced4261d17a07916f43f5b8e\` |
| actions/upload-artifact | 7.0.2 | \`c2acdedd35a8824a1552c7137f8c18288c3ea469\` |
| actions/setup-node | 7.1.0 | \`949feb2413d6458794dcd2491c4babbbce0c15c1\` |
| hashicorp/setup-terraform | 4.0.1 | \`b75000b53e9ce4de2b4712237bbdb711bdc92aba\` |
| peter-evans/create-pull-request | 8.0.0 | \`86c87cfdd87dd582eb8b8f226cfec4e09d825326\` |
| github/codeql-action/upload-sarif | 4.39.1 | \`9b3254085494b55a0f7c4c2b3d2d52cc712ce370\` |
| pypa/gh-action-pypi-publish | pinned upstream commit | \`2442bad8f54b06a326f3030ef5e6a7a674118557\` |

External CLI tools are separately pinned and verified:

- OPA: \`v1.22.0\`; download from the versioned GitHub release and verify the published SHA-256 sidecar before installation.
- kubeconform: \`v0.7.0\`; Linux AMD64 archive SHA-256 is verified in \`.github/workflows/infra-validation.yml\`.
- ExternalSecret JSON schema: vendored from \`datreeio/CRDs-catalog\` commit \`3eb90d47aba8d61919d4419dd38301536e32a94b\`.

Update policy: review upstream release notes and action source before changing a pin. Do not replace a SHA with a mutable major tag. After updating a pin, verify the action's inputs, runtime compatibility, and workflow permissions.
