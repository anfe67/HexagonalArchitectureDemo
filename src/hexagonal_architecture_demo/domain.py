"""Domain model: the center of the hexagon. No I/O, no frameworks."""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class DomainError(Exception):
    """Base for domain-level errors."""


class InvalidEmailError(DomainError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Invalid email: {email!r}")
        self.email = email


class DuplicateEmailError(DomainError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: {email!r}")
        self.email = email


@dataclass(frozen=True)
class User:
    """Immutable domain entity.

    Invariant (enforced by the domain, not the DB): email is normalized to lowercase.
    """

    email: str
    name: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        normalized = self.email.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise InvalidEmailError(self.email)
        object.__setattr__(self, "email", normalized)  # frozen dataclass


@dataclass(frozen=True)
class RegisterResult:
    """Value object returned by the register use case."""

    user: User
    created: bool