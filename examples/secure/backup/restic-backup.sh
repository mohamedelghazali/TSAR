#!/bin/bash
# TSAR reference: encrypted, deduplicated backup with Restic.
set -euo pipefail

export RESTIC_REPOSITORY="${RESTIC_REPOSITORY:?must be set}"
export RESTIC_PASSWORD_FILE="/etc/restic/password"
export AWS_PROFILE="${AWS_PROFILE:-backup}"
export RESTIC_CACHE_DIR="/var/cache/restic"

BACKUP_PATHS=(
  "/var/lib/postgresql"
  "/srv/app/data"
  "/etc"
)

EXCLUDES=(
  "--exclude=/var/lib/postgresql/*/main/pg_wal"
  "--exclude-caches"
  "--exclude-if-present=.nobackup"
)

restic snapshots >/dev/null 2>&1 || restic init

restic backup "${BACKUP_PATHS[@]}" "${EXCLUDES[@]}" \
  --tag "daily" \
  --tag "host:$(hostname -s)" \
  --compression max

restic forget \
  --keep-daily 30 \
  --keep-weekly 12 \
  --keep-monthly 24 \
  --keep-yearly 7 \
  --prune

restic check --read-data-subset=5%

restic snapshots --json | sha256sum > /var/log/restic-manifest.sha256