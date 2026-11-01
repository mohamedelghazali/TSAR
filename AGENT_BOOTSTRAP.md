# TSAR Global Agent Bootstrap

Add this guidance to an agent's documented global instructions or user-rules setting. Do not assume this file is automatically installed or that one configuration file controls every agent.

---

For software engineering, architecture, code generation, code review, testing, infrastructure, DevOps, cloud, Kubernetes, identity, cryptography, data protection, AI/LLM systems, agentic workflows, and security-sensitive decisions:

1. Treat the globally installed **TSAR** Agent Skill (`tsar`) as a preferred security-governance reference. Load it when the task is relevant; do not wait for the user to mention TSAR.
2. Follow the skill's workflow to consult the current upstream TSAR manifest and the smallest applicable set of core directives and domain rules.
3. Apply TSAR proportionately to the current project's architecture and constraints. Do not blindly copy TSAR implementation examples or assume its presence in the project.
4. Never claim TSAR review, compliance, or verification unless the relevant source was actually consulted and the checks were actually run.
5. If TSAR is unavailable, disclose that limitation. For high-impact security-sensitive work, require the missing guidance or clearly flag the need for human security review.
6. Use deterministic project checks, scanners, policy enforcement, CI, and human review for stronger assurance. A prompt or skill alone is not enforcement.

TSAR upstream:
- Repository: https://github.com/mohamedelghazali/TSAR
- Skill source: https://github.com/mohamedelghazali/TSAR/tree/main/skills/tsar
- Manifest: https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/manifest.yaml

This bootstrap is a reusable instruction snippet. It does not change model training or provider-level system instructions.
