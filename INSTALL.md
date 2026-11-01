# Install TSAR

## Recommended global installation

For agents with shell access, Node.js/npm, and permission to install global skills:

```bash
npx skills add mohamedelghazali/TSAR -g --all
```

This asks the Vercel Skills CLI to install every valid skill discovered in this repository to all agents it detects, using global scope. Actual support varies by agent; the CLI reports unsupported targets.

## Verify

```bash
npx skills ls -g
```

Expected TSAR skill names:

- `tsar`
- `crypto-inventory`
- `secret-scanner`
- `secure-review`
- `threat-modeler`

## Update

```bash
npx skills check
npx skills update -g
```

Updates are explicit; do not assume an installed skill is live-synchronized with GitHub.

## No shell or no global-skill support?

Read [ONBOARDING.md](ONBOARDING.md) and [Universal Agent Onboarding](docs/universal-agent-onboarding.md). Load the applicable TSAR directives for the current task, and report honestly that persistent installation was unavailable. Do not invent settings paths or silently modify unrelated configuration.

See [Vercel Skills CLI documentation](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) for current command behavior.
