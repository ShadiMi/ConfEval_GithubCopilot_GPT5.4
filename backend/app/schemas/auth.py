from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import APIModel, TokenPair
from app.schemas.user import UserSummary


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=16)


class PendingReviewerSummary(APIModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: str
    affiliation: str | None
    created_at: datetime
    cv_file_name: str | None = None


class PendingReviewerListResponse(APIModel):
    users: list[PendingReviewerSummary]


class ReviewerApprovalDecisionRequest(BaseModel):
    approved: bool
    reason: str | None = Field(default=None, max_length=1000)


class ReviewerApprovalDecisionResponse(APIModel):
    user: UserSummary
    tokens: TokenPair | None = None
