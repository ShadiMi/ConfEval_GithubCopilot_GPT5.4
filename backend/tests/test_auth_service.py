from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserLoginRequest, UserRegisterRequest
from app.services.auth_service import AuthService
from app.services.user_service import UserService


@pytest.fixture
def db_session() -> Mock:
    return Mock()


def test_register_reviewer_requires_approval_and_notifies_admins(db_session: Mock) -> None:
    service = AuthService(db_session)
    service.notifications = Mock()

    def scalar_side_effect(statement):
        column_name = statement.whereclause.left.name
        if column_name in {"email", "id_number"}:
            return None
        return None

    db_session.scalar.side_effect = scalar_side_effect

    payload = UserRegisterRequest(
        email="reviewer@example.com",
        password="averysecurepass",
        full_name="Reviewer Example",
        role=UserRole.INTERNAL_REVIEWER,
        affiliation=None,
    )

    user = service.register_user(payload)

    assert user.requires_manual_approval is True
    assert user.is_approved is False
    service.notifications.notify_admins_of_pending_reviewer.assert_called_once_with(user)
    db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_register_external_reviewer_stores_cv_and_notifies_admins(db_session: Mock) -> None:
    service = AuthService(db_session)
    service.notifications = Mock()
    service.files = Mock()
    service.files.store_reviewer_cv = AsyncMock(return_value=None)

    def scalar_side_effect(statement):
        column_name = statement.whereclause.left.name
        if column_name in {"email", "id_number"}:
            return None
        return None

    db_session.scalar.side_effect = scalar_side_effect

    payload = UserRegisterRequest(
        email="external@example.com",
        password="averysecurepass",
        full_name="External Reviewer",
        role=UserRole.EXTERNAL_REVIEWER,
        affiliation="External University",
    )

    upload = Mock()

    user = await service.register_external_reviewer(payload, upload)

    assert user.is_approved is False
    assert user.requires_manual_approval is True
    db_session.flush.assert_called_once()
    service.files.store_reviewer_cv.assert_awaited_once_with(user=user, upload=upload)
    service.notifications.notify_admins_of_pending_reviewer.assert_called_once_with(user)
    db_session.commit.assert_called_once()


def test_register_user_rejects_duplicate_id_number(db_session: Mock) -> None:
    service = AuthService(db_session)

    def scalar_side_effect(statement):
        column_name = statement.whereclause.left.name
        if column_name == "email":
            return None
        if column_name == "id_number":
            return User(
                id=uuid4(),
                email="existing@example.com",
                full_name="Existing User",
                role=UserRole.STUDENT,
                id_number="123456789",
                is_active=True,
                is_approved=True,
                requires_manual_approval=False,
            )
        return None

    db_session.scalar.side_effect = scalar_side_effect

    payload = UserRegisterRequest(
        email="student@example.com",
        password="averysecurepass",
        full_name="Student Example",
        role=UserRole.STUDENT,
        id_number="123456789",
        affiliation="SCE",
    )

    with pytest.raises(ValueError, match="ID number is already registered"):
        service.register_user(payload)

    db_session.add.assert_not_called()
    db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_register_external_reviewer_translates_duplicate_id_integrity_error(db_session: Mock) -> None:
    service = AuthService(db_session)
    service.notifications = Mock()
    service.files = Mock()
    service.files.store_reviewer_cv = AsyncMock(return_value=None)

    def scalar_side_effect(statement):
        column_name = statement.whereclause.left.name
        if column_name in {"email", "id_number"}:
            return None
        return None

    db_session.scalar.side_effect = scalar_side_effect
    db_session.flush.side_effect = IntegrityError("INSERT INTO users ...", {}, Exception("duplicate key value"))

    payload = UserRegisterRequest(
        email="external@example.com",
        password="averysecurepass",
        full_name="External Reviewer",
        role=UserRole.EXTERNAL_REVIEWER,
        id_number="123456789",
        affiliation="External University",
    )

    with pytest.raises(ValueError, match="ID number is already registered"):
        await service.register_external_reviewer(payload, Mock())

    db_session.rollback.assert_called_once()


def test_login_rejects_unapproved_reviewer(db_session: Mock) -> None:
    service = AuthService(db_session)
    reviewer = User(
        id=uuid4(),
        email="reviewer@example.com",
        password_hash="hashed",
        full_name="Reviewer Example",
        role=UserRole.EXTERNAL_REVIEWER,
        is_active=True,
        is_approved=False,
        requires_manual_approval=True,
    )
    db_session.scalar.return_value = reviewer

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("app.services.auth_service.verify_password", lambda password, password_hash: True)
        with pytest.raises(PermissionError, match="pending approval"):
            service.login_user(
                UserLoginRequest(email="reviewer@example.com", password="averysecurepass")
            )


def test_login_accepts_short_password_input_and_delegates_to_auth_check(db_session: Mock) -> None:
    service = AuthService(db_session)
    db_session.scalar.return_value = None

    with pytest.raises(ValueError, match="Invalid credentials"):
        service.login_user(UserLoginRequest(email="missing@example.com", password="short"))


def test_refresh_rejects_inactive_user(db_session: Mock) -> None:
    service = AuthService(db_session)
    user = User(
        id=uuid4(),
        email="student@example.com",
        password_hash="hashed",
        full_name="Student Example",
        role=UserRole.STUDENT,
        is_active=False,
        is_approved=True,
        requires_manual_approval=False,
    )
    db_session.scalar.return_value = user

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "app.services.auth_service.decode_token",
            lambda token, expected_type: {"sub": str(user.id), "role": user.role.value, "type": expected_type},
        )
        with pytest.raises(PermissionError, match="inactive"):
            service.refresh_tokens("refresh-token")


def test_admin_can_approve_reviewer(db_session: Mock) -> None:
    service = UserService(db_session)
    service.notifications = Mock()

    admin = User(
        id=uuid4(),
        email="admin@example.com",
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )
    reviewer = User(
        id=uuid4(),
        email="reviewer@example.com",
        full_name="Reviewer Example",
        role=UserRole.INTERNAL_REVIEWER,
        is_active=True,
        is_approved=False,
        requires_manual_approval=True,
    )
    db_session.get.return_value = reviewer

    updated = service.decide_reviewer(actor=admin, user_id=reviewer.id, approved=True, reason="CV accepted")

    assert updated.is_approved is True
    service.notifications.notify_reviewer_decision.assert_called_once_with(
        reviewer,
        approved=True,
        reason="CV accepted",
    )
    db_session.commit.assert_called_once()
