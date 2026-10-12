"""Composition root: the ONE place concrete adapters are chosen and wired.

Run:  uv run python -m hexdemo.main "Alice <alice@example.com>" --db sqlite:///users.db
      uv run python -m hexdemo.main "alice@example.com" Alice --db memory://
"""


import argparse
import sys

from sqlalchemy import create_engine

from .adapters.in_memory import InMemoryUserRepository
from .adapters.sqlalchemy_repo import SqlUserRepository
from .domain import DomainError
from .ports import UserRepository
from .use_cases import RegisterUser


def build_repository(url: str) -> UserRepository:
    """Adapter factory. Add new keys here when you add adapters — the core
    never changes."""
    if url.startswith("sqlite"):
        engine = create_engine(url, future=True)
        return SqlUserRepository(engine)
    if url.startswith("postgresql"):
        engine = create_engine(url, future=True)
        return SqlUserRepository(engine)  # same port, production-grade URL
    raise NotImplementedError(f"No adapter registered for URL {url!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hexdemo: register a user")
    parser.add_argument("email")
    parser.add_argument("name")
    parser.add_argument("--db", default="sqlite:///users.db")
    args = parser.parse_args(argv)

    if args.db == "memory://":
        repository: UserRepository = InMemoryUserRepository()
    else:
        repository = build_repository(args.db)
        if isinstance(repository, SqlUserRepository):
            repository.create_schema()

    use_case = RegisterUser(repository)

    try:
        result = use_case.register(args.email, args.name)
    except DomainError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"{'created ' if result.created else 'existing'} user {result.user.email} ({result.user.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())