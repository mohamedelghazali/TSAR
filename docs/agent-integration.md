# Agent Integration Guide

TSAR uses one security-governance instruction source for every supported model and agent:

- Canonical instructions: [prompts/universal.md](../prompts/universal.md)
- Compatibility profiles: [integrations/agent-profiles.json](../integrations/agent-profiles.json)
- Compatibility matrix: [agent-compatibility-matrix.md](agent-compatibility-matrix.md)

## Setup

1. Read the matching profile by agent key in integrations/agent-profiles.json.
2. Load the exact contents of prompts/universal.md through the product's supported system, project, repository, or agent-instructions mechanism.
3. Do not substitute a legacy prompts/<agent>.md pointer for the canonical file; those paths exist only to preserve old links.
4. Pin TSAR to an immutable commit and follow the mandatory upstream preflight in the universal instructions.
5. Keep the actual integration assurance level honest. Loading instructions alone is E0/E1, not technical enforcement.

## Platform-specific compatibility

The profile registry records only delivery metadata and optional native adapters. For example:

- **Claude Code:** load the universal instructions through CLAUDE.md; the optional hook profile at integrations/claude-code/settings.json is a separate, product-specific control with its own documented scope and tests.
- **GitHub Copilot:** place the universal instructions in .github/copilot-instructions.md using the repository instruction mechanism supported by the installed product version.
- **Cursor / Windsurf:** configure the universal instructions through the current workspace/project rules mechanism supported by the installed version.
- **Chat/model interfaces:** place the universal instructions in the supported system-instructions field.
- **Other agent hosts:** use their supported agent/project context mechanism as recorded in the profile registry.

Do not create a second security policy for a provider. If a platform needs a native hook, tool dispatcher, or lifecycle adapter, implement it as a small separate integration, preserve the universal policy unchanged, and test the adapter independently. If a platform does not expose a supported interception mechanism, do not claim that prompts prevent unsafe actions.

## Mandatory enforcement contract

For lifecycle enforcement, fail-closed behavior, tool boundaries, and assurance levels, follow [Mandatory Agent Adoption and Enforcement Contract](mandatory-agent-enforcement.md). Prompt compliance is not guaranteed. Use TSAR scanners, policy gates, CI, host-side controls, and human review for stronger assurance.

## Enforcement limitations

- Instruction loading is not provider authentication or runtime proof.
- A native adapter proves only the exact host path and events covered by its tests.
- Shared CI validates TSAR's own artifacts and deterministic checks; it must not claim that all 15 external providers were invoked.
- Run live conformance only with an authenticated, supported environment and record unavailable tests as NOT_RUN or BLOCKED, never PASS.
