"""Outbound adapter: in-memory repository (unit tests / demos)."""

from ..domain import User
from ..ports import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._by_email: dict[str, User] = {}

    def find_by_email(self, email: str) -> User | None:
        return self._by_email.get(email.strip().lower())

    def save(self, user: User) -> None:
        self._by_email[user.email] = user  # upsert by design
