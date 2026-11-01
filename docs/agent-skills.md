# Install TSAR as a Global Agent Skill

TSAR publishes an Agent Skills-compatible skill at `skills/tsar/SKILL.md`. It is designed to be installed once for compatible coding agents and discovered across projects.

## Install globally for all detected agents

```bash
npx skills add mohamedelghazali/TSAR -g --all
```

The flags mean:
- `-g` / `--global`: install in the user's global skill locations rather than the current project.
- `--all`: install all skills found in this repository to all agents detected by the CLI, without interactive selection.

To list the repository's available skills without installing:

```bash
npx skills add mohamedelghazali/TSAR --list
```

To verify global installation:

```bash
npx skills ls -g
```

To check for updates and update global skills after TSAR changes:

```bash
npx skills check
npx skills update -g
```

## What global installation provides

The TSAR skill becomes available to compatible agents in other projects under the global scope. Agents generally decide when to load a skill using its name and description, task context, and their own skill-discovery behavior.

## Important: global does not mean forced on every turn

Installing a skill globally does not modify every agent's system prompt, train the model, or guarantee that TSAR is consulted for every unrelated task. The skill's description is intentionally broad across software engineering and security work so compatible agents can discover it when relevant.

For stronger always-on behavior, configure each agent's supported global instruction file to tell it to consult the TSAR skill for software engineering and security tasks. The filename and global configuration location differ by agent and operating system; follow current provider documentation. Do not assume one global instruction file controls every agent.

## Keep installations current

The CLI generally installs a local copy or link according to the agent and platform. After updating TSAR, rerun the install/update command and verify the installed copy. A global install is not a promise of live synchronization with GitHub.

## Enforcement

The skill is instruction-level guidance. For deterministic checks, also use TSAR's scanners, hooks, policy artifacts, CI workflows, and human security review as appropriate. See [Agent Compatibility Matrix](agent-compatibility-matrix.md), [Agent Integration](agent-integration.md), and [Release Qualification](release-qualification.md).
