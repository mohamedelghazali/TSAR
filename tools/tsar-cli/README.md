# TSAR CLI

## Commands
| Command | Description |
|---|---|
| `tsar scan [path] [--format text\|sarif]` | Secret + secure review |
| `tsar inventory [path]` | Cryptographic inventory |
| `tsar lint` | Validate TSAR rules |
| `tsar version` | Compare local/remote manifest version |
| `tsar drift` | Detect drift between local and remote manifest |
| `tsar threat-model <file>` | STRIDE threat model |
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
tsar init . --agent cursor
```

## Exit Codes
- 0: clean.
- 1: findings or drift.
- 2: tooling error.
