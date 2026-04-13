from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import FileAssetKind, ProjectStatus
from app.schemas.common import APIModel
from app.schemas.user import UserSummary
from app.schemas.team import TeamInvitationResponse


class ProjectDecisionRequest(BaseModel):
    approved: bool
    poster_number: str | None = Field(default=None, max_length=50)
    reason: str | None = Field(default=None, max_length=1000)


class ProjectAttachmentSummary(APIModel):
    id: UUID
    kind: FileAssetKind
    file_name: str
    content_type: str
    size_bytes: int


class ProjectSummary(APIModel):
    id: UUID
    title: str
    description: str
    status: ProjectStatus
    mentor_email: EmailStr | None
    poster_number: str | None
    edits_after_approval: bool
    created_at: datetime
    owner: UserSummary
    team_members: list[UserSummary]
    invitations: list[TeamInvitationResponse]
    attachments: list[ProjectAttachmentSummary]


class ProjectListResponse(APIModel):
    projects: list[ProjectSummary]
