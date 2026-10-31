# Extended FAQ

## Is TSAR an antivirus?
No. TSAR is a governance layer that constrains AI-generated code and enforces security patterns. It does not detect or remove malware at runtime.

## Can TSAR guarantee 100% security?
No. No system can. TSAR reduces attack surface, improves consistency, and produces evidence. Residual risk remains and requires human review.

## Does TSAR replace SAST?
No. TSAR's scanners are lightweight pre-commit checks. They complement dedicated SAST tools like Semgrep, CodeQL, and SonarQube. Use all three.

## How does TSAR stay current?
A GitHub Actions workflow runs daily, fetches upstream standards, bumps the manifest version, and opens a PR for review.

## What if an agent ignores TSAR rules?
The scanner detects violations at commit time. If the agent bypasses the prompt, the pre-commit hook and CI still block the commit. Investigate why the agent did not comply and update the prompt or the enforcement level.

## Can I use TSAR offline?
Yes. Run `tsar init` to vendor all rules locally under `.tsar/`. The prompt files reference the local path in offline mode.

## How do I add a rule?
1. Create `rules/<domain>/<name>.md`.
2. Reference it in `manifest.yaml`.
3. Add a test in `tests/test_<domain>_rules.py`.
4. Run `tsar lint`.
5. Open a PR.

## How do I add an agent?
1. Create `prompts/<agent>.md` following existing patterns.
2. Add the agent to `docs/agent-compatibility-matrix.md`.
3. Add it to `tools/tsar-cli/tsar.py` in the `--agent` choices.
4. Update README.

## How do I handle false positives?
1. Document the finding with justification.
2. Add a suppression rule with expiry (default 90 days).
3. Add a test that would catch the pattern if it appears.
4. Review suppressions quarterly.

## Can TSAR be customized per project?
Yes. Fork the repository or create a project-specific overlay directory that extends the manifest. Rules can be added, replaced, or suppressed per project.

## What does "fail closed" mean in practice?
If the manifest cannot be fetched, or rules cannot be loaded:
- The agent enters ADVISORY mode.
- Tier-1 work (auth, crypto, payments, health) is refused.
- All other output is marked "requires manual security review".
- The agent does not silently fall back to unsafe defaults.

## How does TSAR handle secrets in logs?
`rules/data/logging-redaction.md` requires redaction at emission. The secure review scanner flags obvious patterns. Runtime redaction must be implemented in the application; TSAR provides the rule and examples.

## Can I use TSAR with GitHub Copilot for Business?
Yes. Place `prompts/github-copilot.md` content in `.github/copilot-instructions.md` at repository root. Copilot reads this file for suggestions in that repository.

## Does TSAR cover infrastructure-as-code?
Yes. `examples/secure/terraform/` shows hardened AWS resources. Policies in `policies/terraform/` enforce encryption and tagging. The orchestrator runs `terraform validate` in CI.

## What about multi-tenant applications?
`rules/database/multi-tenant.md` requires RLS or equivalent, tests for cross-tenant access, and tenant-scoped caches. `examples/secure/database/` provides a working RLS schema.

## How does TSAR handle post-quantum cryptography?
`rules/crypto/post-quantum.md` and `rules/quantum/` define a hybrid approach: X25519+ML-KEM-768 for key exchange, Ed25519+ML-DSA-44 for signatures. Migration milestones follow NIST IR 8547.

## What if an agent generates code that "looks" secure but is vulnerable?
No pattern-based scanner catches everything. Combine TSAR with:
- Formal verification for crypto.
- Manual penetration testing for Tier-1.
- Fuzzing for parsers and protocols.
- Threat hunting for runtime.

## Can TSAR be used by non-English teams?
The repository is English-only by design to ensure consistency across tools and agents. Localized documentation can be added as a fork without changing the core rules.

## How is TSAR licensed?
See `LICENSE` at the repository root.

## How do I report a security issue in TSAR itself?
See `SECURITY.md`. Do not open public issues for exploitable findings.

## Where can I get help?
Open a GitHub Discussion for general questions. Open an issue for bugs or feature requests. For sensitive matters, use the private security contact.
