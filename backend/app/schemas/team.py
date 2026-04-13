from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import TeamInvitationStatus
from app.schemas.common import APIModel
from app.schemas.user import UserSummary


class TeamInvitationCreateRequest(BaseModel):
    email: EmailStr


class TeamInvitationResponse(APIModel):
    id: UUID
    email: EmailStr
    status: TeamInvitationStatus
    token: str
    expires_at: datetime
    invited_user_id: UUID | None


class ProjectTeamResponse(APIModel):
    project_id: UUID
    owner: UserSummary
    team_members: list[UserSummary]
    pending_invitations: list[TeamInvitationResponse]


class PendingInvitationListResponse(APIModel):
    invitations: list[TeamInvitationResponse]


class InvitationDecisionRequest(BaseModel):
    accept: bool = Field(default=True)
