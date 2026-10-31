#!/bin/bash
# TSAR reference: quarterly restore test into isolated environment.
set -euo pipefail

export RESTIC_REPOSITORY="${RESTIC_REPOSITORY:?must be set}"
export RESTIC_PASSWORD_FILE="/etc/restic/password"

SNAPSHOT_ID="${1:?usage: restore-test.sh <snapshot-id>}"
TARGET_DIR="/mnt/restore-test-$(date +%Y%m%d-%H%M%S)"

mkdir -p "$TARGET_DIR"
restic restore "$SNAPSHOT_ID" --target "$TARGET_DIR" --verify

EXPECTED_HASH="$(restic snapshots --json | jq -r --arg id "$SNAPSHOT_ID" '.[] | select(.id==$id) | .id')"
ACTUAL="$(find "$TARGET_DIR" -type f -exec sha256sum {} + | sort | sha256sum | cut -d' ' -f1)"

echo "Snapshot: $SNAPSHOT_ID"
echo "Restored to: $TARGET_DIR"
echo "Aggregate hash: $ACTUAL"

if [ -z "$EXPECTED_HASH" ]; then
  echo "FAIL: snapshot not found"
  exit 1
fi

echo "PASS: restore completed; validate application startup manually before rejoining production"