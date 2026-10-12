"""Outbound adapter: SQLAlchemy repository (the 'DB connection' side).

The ONLY place in the project that knows SQLAlchemy exists.
Uses sqlalchemy.Uuid: native UUID on Postgres, CHAR(32) on SQLite —
one mapping that works cross-dialect.
"""

from __future__ import annotations

import uuid

from sqlalchemy import String, UniqueConstraint, Uuid, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from ..domain import DuplicateEmailError, User
from ..ports import UserRepository


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    """Row model (adapter vocabulary), deliberately distinct from domain.User."""

    __tablename__ = "users"
    __table_args__ = (
        # DB-level uniqueness: last line of defense, independent of Python checks.
        UniqueConstraint("email", name="uq_users_email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)


class SqlUserRepository(UserRepository):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._sessions = sessionmaker(bind=engine, expire_on_commit=False)

    def create_schema(self) -> None:
        """Schema management is an adapter concern, not a domain concern."""
        Base.metadata.create_all(self._engine)

    def dispose(self) -> None:
        self._engine.dispose()

    @staticmethod
    def _to_row(user: User) -> UserRow:
        return UserRow(id=user.id, email=user.email, name=user.name)

    @staticmethod
    def _to_domain(row: UserRow) -> User:
        return User(email=row.email, name=row.name, id=row.id)

    def find_by_email(self, email: str) -> User | None:
        with self._sessions() as session:
            row = session.scalar(select(UserRow).where(UserRow.email == email.strip().lower()))
        return self._to_domain(row) if row is not None else None

    def save(self, user: User) -> None:
        """Idempotent upsert.

        Pre-check gives a readable domain error; IntegrityError is still caught
        because a concurrent insert can win the race between check and write.
        """
        with self._sessions() as session:
            existing = session.scalar(select(UserRow).where(UserRow.email == user.email))
            if existing is not None:
                return  # already there -> idempotent

            session.add(self._to_row(user))
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise DuplicateEmailError(user.email) from exc
            except SQLAlchemyError:
                session.rollback()
                raise
