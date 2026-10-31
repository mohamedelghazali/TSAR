# Endpoint Detection and Response (EDR)

## Deployment
- All endpoints (laptops, servers, containers, cloud workloads).
- Agents tamper-protected; uninstall requires admin approval.
- Centralized management with RBAC.

## Detection
- Behavioral rules tuned per environment.
- MITRE ATT&CK coverage mapped.
- Alerts routed to SIEM with correlation.

## Response
- Automated isolation for confirmed malicious activity.
- Playbooks for common scenarios (ransomware, lateral movement).
- Forensic snapshot before remediation.

## Telemetry
- Process, file, network, registry events retained >= 30 days.
- Full packet capture on alert (where supported).
- Telemetry forwarded to SIEM.

## Health
- Agent health monitored; alert on offline > 24 hours.
- Version drift alerting.
- Coverage reports per asset inventory.

## Forbidden
- Endpoints without EDR in production.
- Disabled tamper protection.
- Unmonitored agent downtime.
