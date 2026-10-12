from __future__ import annotations

import pytest
from hexagonal_architecture_demo.adapters.in_memory import InMemoryUserRepository
from hexagonal_architecture_demo.adapters.sqlalchemy_repo import Base, SqlUserRepository
from hexagonal_architecture_demo.use_cases import RegisterUser
from sqlalchemy import create_engine

# ---------- unit-level fixtures (no DB at all) ----------


@pytest.fixture
def in_memory_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def use_case(in_memory_repo: InMemoryUserRepository) -> RegisterUser:
    return RegisterUser(in_memory_repo)


# ---------- adapter fixtures (SQLite in-memory, fresh per test) ----------


@pytest.fixture
def sql_engine():
    engine = create_engine("sqlite://", future=True)  # brand-new DB per test
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sql_repo(sql_engine) -> SqlUserRepository:
    return SqlUserRepository(sql_engine)


@pytest.fixture
def sql_use_case(sql_repo: SqlUserRepository) -> RegisterUser:
    return RegisterUser(sql_repo)
