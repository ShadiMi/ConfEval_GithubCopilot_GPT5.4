from unittest.mock import Mock
from uuid import uuid4

from app.models.enums import ProjectStatus, UserRole
from app.models.project import Project
from app.models.user import User
from app.services.project_service import ProjectService


def test_admin_can_approve_project_and_notify_owner() -> None:
    db = Mock()
    service = ProjectService(db)
    service.notifications = Mock()
    service.get_project = Mock()

    admin = User(
        id=uuid4(),
        email="admin@example.com",
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )
    owner = User(
        id=uuid4(),
        email="student@example.com",
        full_name="Student User",
        role=UserRole.STUDENT,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )
    project = Project(
        id=uuid4(),
        title="Project Alpha",
        description="Description",
        owner=owner,
        status=ProjectStatus.PENDING,
    )
    service.get_project.return_value = project

    updated = service.decide_project(
        actor=admin,
        project_id=project.id,
        approved=True,
        poster_number="A-12",
        reason="Ready for review",
    )

    assert updated.status == ProjectStatus.APPROVED
    assert updated.poster_number == "A-12"
    service.notifications.create_notification.assert_called_once()
    db.commit.assert_called_once()
