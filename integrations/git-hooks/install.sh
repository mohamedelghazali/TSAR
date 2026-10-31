#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK="$REPO_ROOT/.git/hooks/pre-commit"

if [ -e "$HOOK" ] && ! grep -q "TSAR" "$HOOK"; then
  cp "$HOOK" "$HOOK.bak.$(date +%s)"
  echo "Backed up existing pre-commit hook"
fi

cp "$REPO_ROOT/integrations/git-hooks/pre-commit" "$HOOK"
chmod +x "$HOOK"

if [ ! -d "$REPO_ROOT/.tsar" ]; then
  git clone --depth 1 https://github.com/mohamedelghazali/TSAR.git "$REPO_ROOT/.tsar"
fi

echo "TSAR pre-commit hook installed"
