#!/usr/bin/env bash
# Scaffolds the hexagonal_architecture_demo project, sets up uv, runs tests, makes the initial git commit.
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p src/hexagonal_architecture_demo/adapters tests

# ... (all file writes from above: pyproject.toml, .gitignore, README.md,
#     src/hexagonal_architecture_demo/*.py, tests/*.py) ...

# --- uv ---
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi
uv python pin 3.12
uv sync --dev          # creates .venv + uv.lock, installs sqlalchemy + pytest

# --- sanity: run the test suite ---
uv run pytest -q

# --- git ---
if ! command -v git >/dev/null 2>&1; then
  echo "git not found — skipping initial commit." >&2
  exit 0
fi
git init -b main
git add .
git -c user.name="${GIT_AUTHOR_NAME:-$(git config user.name || echo dev)}" \
      commit -m "hexagonal_architecture_demo: ports & adapters demo (domain, use case, in-memory + SQLAlchemy adapters, pytest)"
echo "Done. Try: uv run python -m hexagonal_architecture_demo.main 'alice@example.com' Alice --db memory://"