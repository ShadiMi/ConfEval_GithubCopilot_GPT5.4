from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.enums import ConferenceStatus, SessionStatus
from app.schemas.common import APIModel, TimestampedResponse
from app.schemas.tag import TagResponse


class StructuredLocationRequest(BaseModel):
    building: str | None = Field(default=None, max_length=50)
    floor: int | None = None
    room: int | None = None
    location_text: str | None = Field(default=None, max_length=255)


class ConferenceCreateRequest(StructuredLocationRequest):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    start_date: date
    end_date: date
    status: ConferenceStatus = ConferenceStatus.DRAFT

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("Conference end date must not be before start date")
        return self


class CriteriaCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    max_score: int = Field(ge=1, le=100)
    weight: float = Field(ge=0.1, le=10.0)
    display_order: int = Field(default=0, ge=0)


class SessionCreateRequest(BaseModel):
    conference_id: UUID | None = None
    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    start_date: date
    end_date: date
    status: SessionStatus = SessionStatus.UPCOMING
    location_text: str = Field(min_length=2, max_length=255)
    max_project_capacity: int = Field(ge=1, le=1000)
    reviewers_per_project: int = Field(default=2, ge=1, le=10)
    tag_ids: list[UUID] = Field(default_factory=list)
    criteria: list[CriteriaCreateRequest] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("Session end date must not be before start date")
        return self


class CriteriaResponse(TimestampedResponse):
    name: str
    description: str | None
    max_score: int
    weight: float
    display_order: int


class SessionResponse(TimestampedResponse):
    conference_id: UUID | None
    name: str
    description: str | None
    start_date: date
    end_date: date
    status: SessionStatus
    location_label: str
    location_text: str | None
    max_project_capacity: int
    reviewers_per_project: int
    tags: list[TagResponse]
    criteria: list[CriteriaResponse]


class ConferenceResponse(TimestampedResponse):
    name: str
    description: str | None
    start_date: date
    end_date: date
    status: ConferenceStatus
    location_label: str
    location_text: str | None
    location_building: str | None
    location_floor: int | None
    location_room: int | None
    sessions: list[SessionResponse]


class ConferenceListResponse(APIModel):
    conferences: list[ConferenceResponse]


class SessionListResponse(APIModel):
    sessions: list[SessionResponse]
