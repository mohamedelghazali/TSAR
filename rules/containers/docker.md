# Docker and OCI Image Security

## Base Image
- Minimal base: `distroless`, `alpine` (audited), or `scratch`.
- No `latest` tag in production; pin by digest (`image@sha256:...`).
- Rebuild monthly to pick up base image patches.

## Dockerfile Rules
- Multi-stage build; final stage contains only runtime artifacts.
- Non-root user: `USER 10001:10001` after creating the user.
- No secrets in `ARG` or `ENV`; use build secrets (`RUN --mount=type=secret`).
- `COPY` specific paths; never `COPY . .` without `.dockerignore`.
- `.dockerignore` excludes `.git`, `node_modules`, `*.env`, `tests/`, `docs/`.
- No `sudo`, no package managers left installed in final image.

## Hardening
- Set `HEALTHCHECK` for orchestrated environments.
- Read-only root filesystem at runtime.
- Drop all capabilities; add only what is required.
- `no-new-privileges` at runtime.
- seccomp profile: `RuntimeDefault` or custom.
- AppArmor/SELinux profile where supported.

## Labels
- `org.opencontainers.image.source` — repository URL.
- `org.opencontainers.image.revision` — commit SHA.
- `org.opencontainers.image.created` — build timestamp.
- `org.opencontainers.image.licenses` — SPDX identifier.

## Forbidden
- `FROM ubuntu:latest`.
- `RUN apt-get install -y ...` without cleanup (`rm -rf /var/lib/apt/lists/*`).
- Secrets in image layers (visible via `docker history`).
- `--privileged` at runtime.
- Mounting the Docker socket inside a container.
