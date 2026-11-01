# TSAR Agent Compatibility

TSAR supports multiple integration paths. They are related but not interchangeable.

## 1. Agent Skills CLI

The Vercel Skills CLI detects supported coding agents in the current environment and installs compatible skills to the requested scope.

Recommended command:

```bash
npx skills add mohamedelghazali/TSAR -g --all
```

- `-g` requests global/user-level installation.
- `--all` requests all valid skills and all agents detected by the CLI.
- The CLI may report agents that do not support global installation.
- The supported-agent list changes over time; consult the [official CLI documentation](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).

## 2. TSAR's native instruction integrations

The [Agent Compatibility Matrix](docs/agent-compatibility-matrix.md) documents TSAR's 15 provider/product-specific instruction files and their project or system-instruction integration paths.

These integrations require the configuration mechanism offered by each product. They are not automatically installed by the Skills CLI and are not privileged provider-level security controls.

## 3. Chat-only models

A model that can only receive a URL and return text, with no repository browsing, shell, filesystem, connector, or persistent-instruction access, cannot install TSAR or change its future sessions. It can read available TSAR content for the current conversation only.

## 4. Persistence and enforcement

- Global skills can be reused across projects by compatible agents within the installing user account.
- Skill activation is controlled by each agent; global installation does not guarantee loading on every turn.
- Global bootstrap instructions must be configured separately through each agent's supported mechanism.
- Scanners, hooks, policy enforcement, CI checks, and human review provide stronger assurance than prompts alone.
