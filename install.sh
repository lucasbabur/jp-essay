#!/usr/bin/env bash
# Link both essay skills into Claude Code and check the gate checker's runtime.
#   ~/.claude/skills/jp-essay/install.sh    run once after cloning; `git pull` updates both skills
set -euo pipefail
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
skills=$HOME/.claude/skills

if [[ $here != "$skills/jp-essay" ]]; then
  echo "jp-essay: clone the repo to $skills/jp-essay first (it is $here)." >&2
  exit 1
fi
ln -sfn "$here/scientific" "$skills/jp-essay-scientific"
chmod +x "$here/check.py"

if ! command -v uv >/dev/null; then
  echo "jp-essay: the gate checker needs uv. Install it with:" >&2
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi
echo "Installed /jp-essay and /jp-essay-scientific. Start a new Claude Code session to use them."
