"""Use-case tests: pure logic, in-memory adapter. No DB anywhere."""

from __future__ import annotations

import uuid

import pytest

from hexagonal_architecture_demo.domain import DuplicateEmailError, InvalidEmailError
from hexagonal_architecture_demo.ports import UserRepository
from hexagonal_architecture_demo.use_cases import RegisterUser


class TestRegisterUser:
    def test_new_user_is_created(self, use_case):
        result = use_case.register("Alice@Example.COM", "Alice")
        assert result.created is True
        assert result.user.email == "alice@example.com"  # normalized by domain
        assert result.user.name == "Alice"
        assert isinstance(result.user.id, uuid.UUID)

    def test_duplicate_returns_existing_without_creating(self, use_case, in_memory_repo):
        first = use_case.register("bob@example.com", "Bob")
        second = use_case.register("bob@example.com", "Bob the Second")

        assert second.created is False
        assert second.user.id == first.user.id
        assert second.user.name == "Bob"  # original name preserved
        assert len(in_memory_repo._by_email) == 1  # exactly one user

    def test_email_is_case_and_whitespace_insensitive(self, use_case):
        use_case.register("  CAROL@Example.com  ", "Carol")
        result = use_case.register("carol@example.com", "Carol Again")
        assert result.created is False
        assert result.user.email == "carol@example.com"

    def test_invalid_email_rejected_by_domain(self, use_case):
        with pytest.raises(InvalidEmailError):
            use_case.register("not-an-email", "Nobody")

    def test_repository_domain_error_propagates(self, in_memory_repo):
        class ExplodingRepo(UserRepository):
            def find_by_email(self, email):
                raise DuplicateEmailError(email)  # simulated adapter fault

            def save(self, user):
                raise AssertionError("should not save when already present")

        use_case = RegisterUser(ExplodingRepo())
        with pytest.raises(DuplicateEmailError):
            use_case.register("zoe@example.com", "Zoe")