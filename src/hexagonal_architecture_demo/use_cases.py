"""Inbound port implementation: the RegisterUser use case."""

from .domain import RegisterResult, User
from .ports import RegisterUserUseCase, UserRepository


class RegisterUser(RegisterUserUseCase):
    def __init__(self, repository: UserRepository) -> None:
        # Dependency injection: the core requests dependencies via the port;
        # the composition root at the edge supplies a concrete adapter.
        self._repository = repository

    def register(self, email: str, name: str) -> RegisterResult:
        normalized = email.strip().lower()

        existing = self._repository.find_by_email(normalized)
        if existing is not None:
            return RegisterResult(user=existing, created=False)

        user = User(email=normalized, name=name)  # may raise InvalidEmailError
        self._repository.save(user)
        return RegisterResult(user=user, created=True)
