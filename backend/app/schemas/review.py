from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ProjectStatus, ReviewStatus
from app.schemas.common import APIModel
from app.schemas.conference import CriteriaResponse
from app.schemas.user import UserSummary


class ProjectReviewerAssignmentRequest(BaseModel):
    reviewer_ids: list[UUID] = Field(default_factory=list)


class ReviewCriterionScoreInput(BaseModel):
    criteria_id: UUID
    score: float = Field(ge=0)


class ReviewUpsertRequest(BaseModel):
    overall_comment: str | None = Field(default=None, max_length=5000)
    criterion_scores: list[ReviewCriterionScoreInput] = Field(default_factory=list)
    submit: bool = False


class ReviewCriterionScoreResponse(APIModel):
    criteria_id: UUID
    criteria_name: str
    description: str | None
    max_score: int
    weight: float
    display_order: int
    score: float


class ReviewResponse(APIModel):
    id: UUID
    project_id: UUID
    reviewer_id: UUID
    session_id: UUID
    status: ReviewStatus
    overall_comment: str | None
    total_score: float | None
    created_at: datetime
    updated_at: datetime
    reviewer: UserSummary
    criterion_scores: list[ReviewCriterionScoreResponse]


class ReviewerAssignedProjectResponse(APIModel):
    id: UUID
    title: str
    description: str
    status: ProjectStatus
    poster_number: str | None
    session_id: UUID
    session_name: str
    owner: UserSummary
    assigned_reviewers: list[UserSummary]
    review_status: ReviewStatus | None
    total_score: float | None
    review_updated_at: datetime | None


class ReviewerAssignedProjectListResponse(APIModel):
    projects: list[ReviewerAssignedProjectResponse]


class AdminProjectAssignmentResponse(APIModel):
    id: UUID
    title: str
    description: str
    status: ProjectStatus
    poster_number: str | None
    session_id: UUID
    session_name: str
    reviewers_per_project: int
    owner: UserSummary
    assigned_reviewers: list[UserSummary]
    eligible_reviewers: list[UserSummary]
    submitted_review_count: int
    average_score: float | None


class AdminProjectAssignmentListResponse(APIModel):
    projects: list[AdminProjectAssignmentResponse]


class ReviewWorkspaceResponse(APIModel):
    project_id: UUID
    project_title: str
    project_description: str
    poster_number: str | None
    session_id: UUID
    session_name: str
    owner: UserSummary
    assigned_reviewers: list[UserSummary]
    criteria: list[CriteriaResponse]
    review: ReviewResponse | None


class ProjectCompletedReviewsResponse(APIModel):
    project_id: UUID
    project_title: str
    submitted_review_count: int
    average_score: float | None
    reviews: list[ReviewResponse]