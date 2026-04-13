from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.enums import NotificationType, UserRole
from app.models.notification import Notification
from app.models.user import User
from app.services.notification_service import NotificationService


def build_user() -> User:
    return User(
        id=uuid4(),
        email="student@example.com",
        full_name="Student Example",
        role=UserRole.STUDENT,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )


def test_create_notification_adds_record() -> None:
    db = Mock()
    service = NotificationService(db)
    user = build_user()

    notification = service.create_notification(
        user=user,
        notification_type=NotificationType.PROJECT_DECISION,
        title="Project approved",
        message="Your project is approved.",
        link="/dashboard/student/projects",
    )

    assert notification.user == user
    assert notification.type == NotificationType.PROJECT_DECISION
    db.add.assert_called_once_with(notification)


def test_mark_as_read_updates_matching_notification() -> None:
    db = Mock()
    service = NotificationService(db)
    user = build_user()
    notification = Notification(
        id=uuid4(),
        user=user,
        user_id=user.id,
        type=NotificationType.REVIEW_COMPLETED,
        title="Review completed",
        message="A review is available.",
        is_read=False,
    )
    db.scalar.return_value = notification

    updated = service.mark_as_read(user=user, notification_id=notification.id)

    assert updated.is_read is True
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(notification)


def test_mark_as_read_rejects_unknown_notification() -> None:
    db = Mock()
    service = NotificationService(db)
    user = build_user()
    db.scalar.return_value = None

    with pytest.raises(ValueError, match="Notification not found"):
        service.mark_as_read(user=user, notification_id=uuid4())


def test_mark_all_as_read_returns_updated_count() -> None:
    db = Mock()
    service = NotificationService(db)
    user = build_user()
    notifications = [
        Notification(
            id=uuid4(),
            user=user,
            user_id=user.id,
            type=NotificationType.REVIEWER_APPLICATION_SUBMITTED,
            title="Application pending",
            message="Pending.",
            is_read=False,
        ),
        Notification(
            id=uuid4(),
            user=user,
            user_id=user.id,
            type=NotificationType.PROJECT_DECISION,
            title="Project updated",
            message="Updated.",
            is_read=False,
        ),
    ]
    db.scalars.return_value = iter(notifications)

    updated_count = service.mark_all_as_read(user)

    assert updated_count == 2
    assert all(notification.is_read for notification in notifications)
    db.commit.assert_called_once()