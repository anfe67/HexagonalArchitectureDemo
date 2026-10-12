"""SQL-adapter tests: things that only make sense with a real engine."""

from __future__ import annotations

import uuid

import pytest
from hexagonal_architecture_demo.adapters.sqlalchemy_repo import Base, SqlUserRepository
from hexagonal_architecture_demo.domain import User
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def fresh_repo() -> SqlUserRepository:
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    repo = SqlUserRepository(engine)
    yield repo
    repo.dispose()


def test_roundtrip_persists_actual_row(fresh_repo: SqlUserRepository):
    user = User(email="katherine@nodale.com", name="Katherine")
    fresh_repo.save(user)

    # Peek at the DB directly: the adapter really wrote what we expect.
    with fresh_repo._engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, email, name FROM users WHERE email = :e"),
            {"e": user.email},
        ).one()
    assert row.email == user.email
    assert row.name == "Katherine"
    assert uuid.UUID(str(row.id)) == user.id  # UUID survives the roundtrip


def test_db_unique_constraint_is_enforced(fresh_repo: SqlUserRepository):
    """The DB itself rejects duplicate emails (defense in depth below the adapter)."""
    user = User(email="race@dupe.io", name="A")
    fresh_repo.save(user)

    with fresh_repo._engine.begin() as conn, pytest.raises(IntegrityError):
        conn.execute(
            text("INSERT INTO users (id, email, name) VALUES (:i, :e, :n)"),
            {"i": str(uuid.uuid4()), "e": user.email, "n": "B"},
        )


def test_use_case_end_to_end_on_sqlite(sql_use_case, sql_repo):
    """Same use case, different adapter — identical behavior."""
    r1 = sql_use_case.register("E2E@Test.org", "E2E")
    r2 = sql_use_case.register("e2e@test.org", "E2E Again")
    assert r1.created is True
    assert r2.created is False
    assert r2.user.id == r1.user.id
    assert sql_repo.find_by_email("e2e@test.org") is not None
