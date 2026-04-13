from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ReviewerApplicationStatus, SessionStatus
from app.schemas.common import APIModel
from app.schemas.user import UserSummary


class ReviewerApplicationCreateRequest(BaseModel):
    session_id: UUID
    cover_message: str | None = Field(default=None, max_length=2000)


class ReviewerApplicationDecisionRequest(BaseModel):
    approved: bool
    decision_notes: str | None = Field(default=None, max_length=2000)


class ReviewerApplicationResponse(APIModel):
    id: UUID
    reviewer_id: UUID
    session_id: UUID
    status: ReviewerApplicationStatus
    session_name: str
    session_status: SessionStatus
    cover_message: str | None
    decision_notes: str | None
    decided_by_id: UUID | None
    created_at: datetime
    updated_at: datetime
    reviewer: UserSummary


class ReviewerApplicationListResponse(APIModel):
    applications: list[ReviewerApplicationResponse]
