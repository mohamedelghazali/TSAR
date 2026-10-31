# FAQ

## Does TSAR guarantee 100% security?
No system can guarantee 100% security. TSAR reduces the attack surface by
enforcing defense-in-depth and failing closed on known-dangerous patterns.
Residual risk depends on the surrounding codebase, deployment, and operations.

## What happens if the manifest fetch fails?
The agent enters ADVISORY mode and marks output for manual security review.
It does not silently proceed with unsafe defaults.

## Can I add custom rules?
Yes. Place them in `rules/`, add to `manifest.yaml`, run `scripts/lint_rules.py`,
and open a PR.

## Can I use TSAR offline?
Yes. Clone the repository into `.tsar/` inside your project and update your
prompt file to read from the local path.

## Does TSAR replace SAST/DAST?
No. TSAR is a governance layer for AI-generated code. Combine it with a
full SAST/DAST/SCA pipeline. TSAR's scanners are lightweight pre-commit checks,
not a replacement for comprehensive static analysis.

## How do rules stay current?
A GitHub Actions workflow runs daily, fetches upstream standards, bumps the
manifest version, and opens a PR. The agent reloads on version mismatch.

## Is there any Arabic text in the repository?
No. The repository is English-only by design.
