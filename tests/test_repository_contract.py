"""Contract tests: the port's behavioral contract, verified on EVERY adapter.

Add a Mongo repository tomorrow -> add it to _factories -> it instantly
inherits the full behavioral guarantee. That's why we test ports, not classes.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine

from hexagonal_architecture_demo.adapters.in_memory import InMemoryUserRepository
from hexagonal_architecture_demo.adapters.sqlalchemy_repo import Base, SqlUserRepository
from hexagonal_architecture_demo.domain import User
from hexagonal_architecture_demo.ports import UserRepository


def _in_memory() -> InMemoryUserRepository:
    return InMemoryUserRepository()


def _sqlalchemy() -> SqlUserRepository:
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    return SqlUserRepository(engine)


_FACTORIES = {"in_memory": _in_memory, "sqlalchemy": _sqlalchemy}


@pytest.fixture(params=list(_FACTORIES))
def repo(request) -> UserRepository:
    r = _FACTORIES[request.param]()
    yield r
    dispose = getattr(r, "dispose", None)
    if callable(dispose):
        dispose()


def test_save_then_find_by_email(repo: UserRepository):
    user = User(email="ada@lovelace.dev", name="Ada")
    repo.save(user)
    found = repo.find_by_email("ada@lovelace.dev")
    assert found is not None
    assert found.id == user.id
    assert found.name == "Ada"


def test_find_missing_returns_none(repo: UserRepository):
    assert repo.find_by_email("ghost@example.com") is None


def test_find_is_case_insensitive(repo: UserRepository):
    user = User(email="grace@hopper.us", name="Grace")
    repo.save(user)
    found = repo.find_by_email("GRACE@HOPPER.US")
    assert found is not None
    assert found.id == user.id


def test_save_is_idempotent_upsert(repo: UserRepository):
    user = User(email="alan@turing.uk", name="Alan")
    repo.save(user)
    repo.save(user)  # must not raise, must not duplicate
    found = repo.find_by_email("alan@turing.uk")
    assert found.id == user.id