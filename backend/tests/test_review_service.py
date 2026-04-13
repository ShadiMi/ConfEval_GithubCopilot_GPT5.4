from unittest.mock import ANY, Mock
from uuid import uuid4

import pytest

from app.models.conference import Criteria, Session
from app.models.enums import ProjectStatus, ReviewStatus, SessionStatus, UserRole
from app.models.project import Project
from app.models.review import Review
from app.models.user import User
from app.services.review_service import ReviewService


def build_user(role: UserRole, email: str, full_name: str) -> User:
    return User(
        id=uuid4(),
        email=email,
        full_name=full_name,
        role=role,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )


def build_project() -> tuple[Project, User, User, User, User]:
    owner = build_user(UserRole.STUDENT, "student@example.com", "Student")
    admin = build_user(UserRole.ADMIN, "admin@example.com", "Admin")
    reviewer = build_user(UserRole.INTERNAL_REVIEWER, "reviewer@example.com", "Reviewer")
    teammate = build_user(UserRole.STUDENT, "teammate@example.com", "Teammate")
    session = Session(
        id=uuid4(),
        name="Poster Session",
        start_date="2026-04-13",
        end_date="2026-04-14",
        status=SessionStatus.ACTIVE,
        location_label="Hall A",
        max_project_capacity=20,
        reviewers_per_project=2,
    )
    criteria = Criteria(
        id=uuid4(),
        session=session,
        session_id=session.id,
        name="Novelty",
        max_score=10,
        weight=1.0,
        display_order=0,
    )
    session.criteria = [criteria]
    session.reviewers = [reviewer]

    project = Project(
        id=uuid4(),
        title="Project Alpha",
        description="Description",
        owner=owner,
        owner_id=owner.id,
        status=ProjectStatus.APPROVED,
        session=session,
        session_id=session.id,
    )
    project.team_members = [teammate]
    project.assigned_reviewers = []
    project.reviews = []
    return project, owner, admin, reviewer, teammate


def test_admin_can_assign_eligible_reviewer() -> None:
    db = Mock()
    service = ReviewService(db)
    service.notifications = Mock()
    project, _, admin, reviewer, _ = build_project()
    service.get_project = Mock(return_value=project)

    updated = service.assign_reviewers(actor=admin, project_id=project.id, reviewer_ids=[reviewer.id])

    assert updated.assigned_reviewers == [reviewer]
    service.notifications.create_notification.assert_called_once()
    db.commit.assert_called_once()


def test_submit_review_requires_all_criteria() -> None:
    db = Mock()
    service = ReviewService(db)
    service.notifications = Mock()
    project, _, _, reviewer, _ = build_project()
    project.assigned_reviewers = [reviewer]
    service.get_reviewer_workspace = Mock(return_value=(project, None))

    with pytest.raises(ValueError):
        service.upsert_review(
            reviewer=reviewer,
            project_id=project.id,
            overall_comment="Looks good",
            criterion_scores=[],
            submit=True,
        )


def test_submit_review_records_score_and_status() -> None:
    db = Mock()
    service = ReviewService(db)
    service.notifications = Mock()
    project, owner, _, reviewer, teammate = build_project()
    project.assigned_reviewers = [reviewer]
    service.get_reviewer_workspace = Mock(return_value=(project, None))

    submitted_review = Review(
        id=uuid4(),
        project=project,
        project_id=project.id,
        reviewer=reviewer,
        reviewer_id=reviewer.id,
        session_id=project.session_id,
        status=ReviewStatus.SUBMITTED,
        total_score=8.5,
    )
    service.get_review = Mock(return_value=submitted_review)

    review = service.upsert_review(
        reviewer=reviewer,
        project_id=project.id,
        overall_comment="Looks good",
        criterion_scores=[(project.session.criteria[0].id, 8.5)],
        submit=True,
    )

    assert review.status == ReviewStatus.SUBMITTED
    assert service.notifications.create_notification.call_count == 2
    service.notifications.create_notification.assert_any_call(
        user=owner,
        notification_type=ANY,
        title="Project review submitted",
        message=f"A completed review is now available for '{project.title}'.",
        link=f"/dashboard/student/projects/{project.id}/reviews",
    )
    service.notifications.create_notification.assert_any_call(
        user=teammate,
        notification_type=ANY,
        title="Project review submitted",
        message=f"A completed review is now available for '{project.title}'.",
        link=f"/dashboard/student/projects/{project.id}/reviews",
    )
    db.commit.assert_called_once()


def test_team_member_can_view_completed_reviews() -> None:
    db = Mock()
    service = ReviewService(db)
    project, _, _, reviewer, teammate = build_project()
    project.reviews = [
        Review(
            id=uuid4(),
            project=project,
            project_id=project.id,
            reviewer=reviewer,
            reviewer_id=reviewer.id,
            session_id=project.session_id,
            status=ReviewStatus.SUBMITTED,
            total_score=9.0,
        )
    ]
    service.get_project = Mock(return_value=project)

    _, reviews, average_score = service.list_project_completed_reviews(actor=teammate, project_id=project.id)

    assert len(reviews) == 1
    assert average_score == 9.0