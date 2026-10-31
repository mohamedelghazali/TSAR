# Forensic Analysis

## Principles
- Analysis on copies, never originals.
- Every action logged with tool version and parameters.
- Findings reproducible by an independent analyst.

## Artifacts
| Category | Artifacts |
|---|---|
| Filesystem | MFT, inodes, journal, deleted files |
| Memory | Processes, network connections, injected code |
| Logs | Auth, web, database, cloud audit |
| Network | PCAP, flow, DNS, proxy |
| Cloud | Control plane audit, data plane access |
| Mobile | App data, keychain, SQLite databases |

## Tools
- Autopsy/Sleuth Kit for disk.
- Volatility for memory.
- Wireshark/Zeek for network.
- Plaso/timesketch for timeline.

## Reporting
- Executive summary.
- Timeline of events.
- Findings with evidence references.
- Confidence levels.
- IOCs extracted for detection.

## Forbidden
- Analysis on original media.
- Findings without evidence.
- Reports without confidence levels.
- Unsupported speculation.
