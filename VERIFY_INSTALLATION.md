# Verify TSAR Installation

Use these checks after installation. Record actual output; do not infer success from a completed command alone.

## 1. Discover skills published by TSAR

```bash
npx skills add mohamedelghazali/TSAR --list
```

Expected names:

- `tsar`
- `crypto-inventory`
- `secret-scanner`
- `secure-review`
- `threat-modeler`

Each skill's `SKILL.md` must begin with YAML frontmatter containing both `name` and `description`. The `name` must match its parent directory.

## 2. Install globally

```bash
npx skills add mohamedelghazali/TSAR -g --all
```

Review the summary for installed agents and unsupported global-install targets.

## 3. Verify installed skills

```bash
npx skills ls -g
```

Confirm that the five TSAR skills appear in the global installation listing. On Windows PowerShell, the canonical shared skill directory commonly resides under:

```powershell
Test-Path "$HOME\.agents\skills\tsar\SKILL.md"
Get-Content "$HOME\.agents\skills\tsar\SKILL.md" -TotalCount 12
```

The exact agent-specific links or directories vary by CLI version and agent.

## 4. Check updates

```bash
npx skills check
npx skills update -g
```

## 5. Smoke-test behavior

Ask the agent to review a small sample for one relevant security topic and report:
- Which TSAR skill it loaded.
- Which manifest and rule files it consulted.
- Which checks it actually ran.
- Which checks it could not run.

A smoke test verifies discovery and workflow invocation only. It is not proof of complete security coverage or compliance.

## 6. Persistence test

Start a new project or session with the same agent and verify that the installed skill is still discoverable. If the agent does not load it automatically, configure [AGENT_BOOTSTRAP.md](AGENT_BOOTSTRAP.md) through its documented global-instructions mechanism, if available.

Do not claim universal always-on behavior. Agents differ in their skill discovery and persistence capabilities.
