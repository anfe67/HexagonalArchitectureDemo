# Hexagonal Architecture Demo — Hexagonal (Ports & Adapters) in Python

Small demo of the hexagonal architecture: a **register user** feature with
one inbound port (use case), one outbound port (user repository), two
driven adapters (in-memory, SQLAlchemy/SQLite), and a composition root.

## Layout
- `src/hexagonal_architecture_demo/domain.py` — entities & errors (the heart, no I/O)
- `src/hexagonal_architecture_demo/ports.py` — inbound/outbound interfaces (the boundaries)
- `src/hexagonal_architecture_demo/use_cases.py` — the register use case (inbound port impl)
- `src/hexagonal_architecture_demo/adapters/` — driven adapters: `in_memory`, `sqlalchemy_repo`
- `src/hexagonal_architecture_demo/main.py` — composition root (CLI driver + wiring)
- `tests/` — use-case unit tests, port contract tests, SQL adapter tests

## Usage (uv)
```bash
uv sync --dev
uv run pytest -v
uv run python -m hexagonal_architecture_demo.main "alice@example.com" Alice --db memory://
uv run python -m hexagonal_architecture_demo.main "alice@example.com" Alice --db sqlite:///users.db