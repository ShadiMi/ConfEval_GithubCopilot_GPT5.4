from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.enums import TeamInvitationStatus, UserRole
from app.models.project import Project, TeamInvitation
from app.models.user import User
from app.services.team_service import TeamService


def build_owner() -> User:
    return User(
        id=uuid4(),
        email="owner@example.com",
        full_name="Owner Student",
        role=UserRole.STUDENT,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )


def test_invite_registered_student_adds_immediately() -> None:
    db = Mock()
    service = TeamService(db)
    owner = build_owner()
    teammate = User(
        id=uuid4(),
        email="mate@example.com",
        full_name="Teammate",
        role=UserRole.STUDENT,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )
    project = Project(id=uuid4(), title="Project", description="Description", owner=owner)
    project.team_members = []
    project.invitations = []
    service.get_project_for_team = Mock(return_value=project)
    db.scalar.return_value = teammate

    updated = service.invite_team_member(actor=owner, project_id=project.id, email=teammate.email)

    assert teammate in updated.team_members
    db.commit.assert_called_once()


def test_invite_unregistered_email_creates_pending_invitation() -> None:
    db = Mock()
    service = TeamService(db)
    owner = build_owner()
    project = Project(id=uuid4(), title="Project", description="Description", owner=owner)
    project.team_members = []
    project.invitations = []
    service.get_project_for_team = Mock(return_value=project)
    db.scalar.return_value = None

    updated = service.invite_team_member(actor=owner, project_id=project.id, email="pending@example.com")

    assert db.add.called
    assert updated.id == project.id
    db.commit.assert_called_once()


def test_accept_invitation_adds_member() -> None:
    db = Mock()
    service = TeamService(db)
    owner = build_owner()
    invitee = User(
        id=uuid4(),
        email="invitee@example.com",
        full_name="Invitee",
        role=UserRole.STUDENT,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )
    project = Project(id=uuid4(), title="Project", description="Description", owner=owner)
    project.team_members = []
    invitation = TeamInvitation(
        id=uuid4(),
        email=invitee.email,
        status=TeamInvitationStatus.PENDING,
        token="token-123",
        project=project,
    )
    db.scalar.return_value = invitation

    result = service.respond_to_invitation(actor=invitee, token="token-123", accept=True)

    assert result.status == TeamInvitationStatus.ACCEPTED
    assert invitee in project.team_members
    db.commit.assert_called_once()


def test_only_owner_or_admin_can_manage_team() -> None:
    db = Mock()
    service = TeamService(db)
    owner = build_owner()
    outsider = User(
        id=uuid4(),
        email="outsider@example.com",
        full_name="Outsider",
        role=UserRole.STUDENT,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )
    project = Project(id=uuid4(), title="Project", description="Description", owner=owner)

    with pytest.raises(PermissionError):
        service.ensure_project_manager(outsider, project)
