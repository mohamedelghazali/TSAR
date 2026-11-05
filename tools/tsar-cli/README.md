# TSAR CLI

## Commands

| Command | Description |
|---|---|
| `tsar scan [path] [--format text\|sarif]` | Secret + secure review |
| `tsar inventory [path]` | Cryptographic inventory |
| `tsar lint` | Validate TSAR rules |
| `tsar version` | Compare local/remote manifest version |
| `tsar drift` | Detect drift between local and remote manifest (legacy version/file-set comparison) |
| `tsar verify-upstream [--domain NAME]` | Pin upstream to one commit, validate manifest and all active paths, and fetch core plus selected domain rules (fail-closed) |
| `tsar threat-model <file>` | STRIDE threat model |
| `tsar lifecycle-plan <task> [--domain NAME] [--impact auto\|standard\|high]` | Create a deterministic lifecycle plan; does not execute or approve work |
| `tsar report [path] [--format html\|json]` | Full report |
| `tsar compliance <framework>` | Compliance reference check |
| `tsar init [path] --agent <name>` | Bootstrap TSAR into a project |

## Examples

```bash
tsar scan .
tsar scan . --format sarif --output results.sarif
tsar report . --format html --output report.html
tsar compliance soc2
tsar drift
tsar verify-upstream --domain api --domain iam
tsar lifecycle-plan "Implement OAuth login API" --domain iam --domain api
tsar lifecycle-start "Implement OAuth login API" --domain iam --domain api --audit-file .tsar/runs/oauth-login.json
tsar init . --agent cursor
```

## Exit Codes

- 0: clean.
- 1: findings or drift.
- 2: verification/tooling failure (preflight fails closed).

## Lifecycle evidence boundaries

`lifecycle-evidence` accepts only non-empty regular evidence files inside the TSAR project root, rejects symlink paths and path traversal, records SHA-256, size, actor label, timestamp, and PASS/FAIL decision, and updates only a PENDING gate. The upstream preflight gate cannot be overridden. The actor label is not authenticated, evidence content is not semantically validated, and the local audit file is not tamper-proof or signed.

Example:

```bash
tsar lifecycle-evidence --audit-file .tsar/runs/run.json --gate core_policy_review --evidence evidence/core-review.md --actor reviewer@example.org --decision PASS
```

## Lifecycle planning boundaries

`lifecycle-plan` is a deterministic planning aid. Keyword classification can miss context or select extra domains; operators must confirm the applicable domains and impact before implementation. A plan is not a security approval, does not execute scanners, and does not mark gates as passed. High-impact tasks require the listed additional review gates.
