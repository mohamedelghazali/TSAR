#!/bin/bash
# TSAR reference: encrypted backup with BorgBackup.
set -euo pipefail

export BORG_REPO="ssh://backup@backup.example.com/./tsar"
export BORG_PASSCOMMAND="cat /etc/borg/passphrase"
export BORG_RSH="ssh -i /etc/borg/id_ed25519 -o StrictHostKeyChecking=yes"

if ! borg info >/dev/null 2>&1; then
  borg init --encryption=repokey-blake2
fi

borg create \
  --compression zstd,10 \
  --exclude-caches \
  --exclude '/home/*/.cache' \
  --exclude '/var/lib/postgresql/*/main/pg_wal' \
  --stats \
  "::tsar-{now:%Y-%m-%dT%H:%M:%S}" \
  /etc /var/lib/postgresql /srv/app/data

borg prune \
  --keep-daily=30 \
  --keep-weekly=12 \
  --keep-monthly=24 \
  --keep-yearly=7 \
  --list

borg check --verify-data