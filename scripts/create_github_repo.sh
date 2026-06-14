#!/usr/bin/env bash
# Create the public GitHub repo and push. Run from the project root on your own
# machine (where `gh` is installed). Requires: gh, git.
set -euo pipefail

# 1. Authenticate once (skip if `gh auth status` already works):
#    gh auth login

# 2. Create the public repo under your account and push the existing commit:
gh repo create reflex-pragmatic-drag-and-drop \
  --public \
  --source . \
  --remote origin \
  --description "Reflex bindings for Atlassian Pragmatic drag and drop (sortable lists, Kanban) in pure Python" \
  --push

echo "Done -> https://github.com/$(gh api user --jq .login)/reflex-pragmatic-drag-and-drop"
