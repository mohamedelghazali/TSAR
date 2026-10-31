# Compliance Mapping

TSAR rules map to major compliance frameworks. Each mapping document lists
controls and the corresponding rule files.

## Frameworks
- [SOC 2](soc2.md) — Trust Services Criteria.
- [ISO 27001:2022](iso27001.md) — Annex A controls.
- [PCI DSS 4.0](pci-dss.md) — Payment card data.
- [HIPAA](hipaa.md) — US healthcare.
- [GDPR](gdpr.md) — EU data protection.

## How to Use
1. Identify the frameworks applicable to your system.
2. For each control, open the corresponding TSAR rule file.
3. Verify the rule is enabled in your agent and CI.
4. Collect evidence from CI logs, signed artifacts, and runbook records.
5. Document exceptions with a risk acceptance.

## Limitations
- TSAR provides technical controls; organizational controls (policies,
  training, physical security) are outside its scope.
- Compliance requires an independent audit; TSAR is evidence, not certification.
- Regulatory requirements vary by jurisdiction; consult legal counsel.
