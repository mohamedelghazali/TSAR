# Container Runtime Security

## Isolation
- gVisor, Kata Containers, or Firecracker for multi-tenant workloads.
- User namespaces enabled where the orchestrator supports it.
- cgroup v2 with memory and CPU limits enforced.

## Runtime Policies
- Falco or Tetragon for runtime threat detection:
  - Unexpected process execution (shell in container).
  - Unexpected network egress.
  - File access outside expected paths.
  - Privilege escalation attempts.
- Alerts forward to SIEM with correlation rules.

## Syscalls
- seccomp profile: `RuntimeDefault` minimum; custom whitelist for high-assurance.
- Block dangerous syscalls: `ptrace`, `mount`, `unshare` (unless required).
- No `CAP_SYS_ADMIN` for application containers.

## Filesystem
- Read-only root filesystem.
- Writable paths via `emptyDir` or explicit volumes.
- No hostPath mounts except audited system components.

## Network
- NetworkPolicy default-deny.
- Egress via explicit allow-list or egress gateway.
- No `hostNetwork`, no `hostPID`, no `hostIPC`.

## Forbidden
- `--privileged` flag.
- `CAP_SYS_ADMIN` for application workloads.
- Docker socket mounted inside a container.
- Containers running as root.
