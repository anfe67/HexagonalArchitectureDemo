"""Ports: the API surface of the hexagon.

An INBOUND port is a use case the outside world may call.
An OUTBOUND port is an interface the core defines and its adapters implement.
"""

# from __future__ import annotations

from abc import ABC, abstractmethod

from .domain import RegisterResult, User


class RegisterUserUseCase(ABC):
    """Inbound port: what drivers (CLI, HTTP, tests) call."""

    @abstractmethod
    def register(self, email: str, name: str) -> RegisterResult:
        """Register *email* under *name*; returns the user and whether it was created."""


class UserRepository(ABC):
    """Outbound port: the core's view of 'the database'.

    The core only knows this interface — not whether it is Postgres, SQLite, or a dict.
    """

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        """Return the user with the given (normalized) email, else None."""

    @abstractmethod
    def save(self, user: User) -> None:
        """Persist the user. Must be idempotent (upsert)."""