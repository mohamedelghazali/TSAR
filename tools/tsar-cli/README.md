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
tsar init . --agent cursor
```

## Exit Codes

- 0: clean.
- 1: findings or drift.
- 2: verification/tooling failure (preflight fails closed).

## Lifecycle planning boundaries

`lifecycle-plan` is a deterministic planning aid. Keyword classification can miss context or select extra domains; operators must confirm the applicable domains and impact before implementation. A plan is not a security approval, does not execute scanners, and does not mark gates as passed. High-impact tasks require the listed additional review gates.
