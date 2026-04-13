from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.conference import Session
from app.models.enums import ReviewerApplicationStatus, SessionStatus, UserRole
from app.models.review import ReviewerApplication
from app.models.user import User
from app.services.application_service import ReviewerApplicationService


def build_reviewer(role: UserRole = UserRole.INTERNAL_REVIEWER) -> User:
    return User(
        id=uuid4(),
        email="reviewer@example.com",
        full_name="Reviewer User",
        role=role,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )


def test_reviewer_can_apply_to_session() -> None:
    db = Mock()
    service = ReviewerApplicationService(db)
    service.notifications = Mock()
    reviewer = build_reviewer()
    session = Session(
        id=uuid4(),
        name="Applied Session",
        start_date="2026-04-13",
        end_date="2026-04-14",
        status=SessionStatus.UPCOMING,
        location_label="Room 101",
        max_project_capacity=10,
        reviewers_per_project=2,
    )
    session.reviewers = []
    service._get_session = Mock(return_value=session)
    service.get_application = Mock(return_value=ReviewerApplication(id=uuid4(), reviewer=reviewer, session=session))
    db.scalar.return_value = None
    db.scalars.return_value = iter([])

    application = service.apply_to_session(reviewer=reviewer, session_id=session.id, cover_message="Interested")

    assert application.reviewer == reviewer
    db.commit.assert_called_once()


def test_admin_approval_assigns_reviewer_to_session() -> None:
    db = Mock()
    service = ReviewerApplicationService(db)
    service.notifications = Mock()
    admin = User(
        id=uuid4(),
        email="admin@example.com",
        full_name="Admin",
        role=UserRole.ADMIN,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )
    reviewer = build_reviewer()
    session = Session(
        id=uuid4(),
        name="Applied Session",
        start_date="2026-04-13",
        end_date="2026-04-14",
        status=SessionStatus.UPCOMING,
        location_label="Room 101",
        max_project_capacity=10,
        reviewers_per_project=2,
    )
    session.reviewers = []
    application = ReviewerApplication(
        id=uuid4(),
        reviewer=reviewer,
        reviewer_id=reviewer.id,
        session=session,
        session_id=session.id,
        status=ReviewerApplicationStatus.PENDING,
    )
    db.scalar.return_value = application

    updated = service.decide_application(
        actor=admin,
        application_id=application.id,
        approved=True,
        decision_notes="Approved",
    )

    assert updated.status == ReviewerApplicationStatus.APPROVED
    assert reviewer in session.reviewers
    db.commit.assert_called_once()


def test_only_reviewers_can_apply() -> None:
    db = Mock()
    service = ReviewerApplicationService(db)
    student = User(
        id=uuid4(),
        email="student@example.com",
        full_name="Student",
        role=UserRole.STUDENT,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )

    with pytest.raises(PermissionError):
        service.apply_to_session(reviewer=student, session_id=uuid4(), cover_message=None)
