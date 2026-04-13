from __future__ import annotations

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import TeamInvitationStatus, UserRole
from app.models.project import Project, TeamInvitation
from app.models.user import User

INVITATION_EXPIRY_DAYS = 14
MAX_ADDITIONAL_TEAM_MEMBERS = 2


class TeamService:
    def __init__(self, db: Session):
        self.db = db

    def get_project_for_team(self, project_id: UUID | str) -> Project:
        project = self.db.scalar(
            select(Project)
            .where(Project.id == UUID(str(project_id)))
            .options(
                selectinload(Project.owner),
                selectinload(Project.team_members),
                selectinload(Project.invitations),
            )
        )
        if project is None:
            raise ValueError("Project not found")
        return project

    def ensure_project_manager(self, actor: User, project: Project) -> None:
        if actor.role == UserRole.ADMIN:
            return
        if actor.id != project.owner_id:
            raise PermissionError("Only the project owner or an admin can manage the team")

    def _current_team_load(self, project: Project) -> int:
        pending = [inv for inv in project.invitations if inv.status == TeamInvitationStatus.PENDING]
        return len(project.team_members) + len(pending)

    def invite_team_member(self, *, actor: User, project_id: UUID | str, email: str) -> Project:
        project = self.get_project_for_team(project_id)
        self.ensure_project_manager(actor, project)
        normalized_email = email.strip().lower()
        if normalized_email == project.owner.email.lower():
            raise ValueError("Project owner cannot be invited as a team member")
        if any(member.email.lower() == normalized_email for member in project.team_members):
            raise ValueError("User is already a team member")
        if any(inv.email.lower() == normalized_email and inv.status == TeamInvitationStatus.PENDING for inv in project.invitations):
            raise ValueError("A pending invitation already exists for that email")
        if self._current_team_load(project) >= MAX_ADDITIONAL_TEAM_MEMBERS:
            raise ValueError("Projects may have at most 2 additional team members")

        existing_user = self.db.scalar(select(User).where(User.email == normalized_email))
        if existing_user is not None:
            if existing_user.role != UserRole.STUDENT:
                raise ValueError("Only registered students can join a project team")
            project.team_members.append(existing_user)
            self.db.commit()
            return self.get_project_for_team(project.id)

        invitation = TeamInvitation(
            project=project,
            email=normalized_email,
            status=TeamInvitationStatus.PENDING,
            token=token_urlsafe(24),
            expires_at=datetime.now(UTC) + timedelta(days=INVITATION_EXPIRY_DAYS),
        )
        self.db.add(invitation)
        self.db.commit()
        return self.get_project_for_team(project.id)

    def list_pending_invitations_for_user(self, user: User) -> list[TeamInvitation]:
        return list(
            self.db.scalars(
                select(TeamInvitation)
                .where(TeamInvitation.email == user.email.lower())
                .where(TeamInvitation.status == TeamInvitationStatus.PENDING)
                .order_by(TeamInvitation.created_at.desc())
            )
        )

    def respond_to_invitation(self, *, actor: User, token: str, accept: bool) -> TeamInvitation:
        invitation = self.db.scalar(
            select(TeamInvitation)
            .where(TeamInvitation.token == token)
            .options(selectinload(TeamInvitation.project).selectinload(Project.team_members))
        )
        if invitation is None:
            raise ValueError("Invitation not found")
        if invitation.status != TeamInvitationStatus.PENDING:
            raise ValueError("Invitation is no longer pending")
        if invitation.email.lower() != actor.email.lower() and actor.role != UserRole.ADMIN:
            raise PermissionError("You cannot respond to this invitation")
        if invitation.expires_at < datetime.now(UTC):
            invitation.status = TeamInvitationStatus.DECLINED
            self.db.commit()
            raise ValueError("Invitation has expired")

        if accept:
            project = invitation.project
            if actor.role != UserRole.STUDENT and actor.role != UserRole.ADMIN:
                raise ValueError("Only student users can accept team invitations")
            if len(project.team_members) >= MAX_ADDITIONAL_TEAM_MEMBERS:
                raise ValueError("The project team is already full")
            if actor not in project.team_members:
                project.team_members.append(actor)
            invitation.status = TeamInvitationStatus.ACCEPTED
            invitation.invited_user_id = actor.id
        else:
            invitation.status = TeamInvitationStatus.DECLINED
            invitation.invited_user_id = actor.id

        self.db.commit()
        self.db.refresh(invitation)
        return invitation
