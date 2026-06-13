from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import UserRole
from app.schemas.common import APIModel, TimestampedResponse


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    role: UserRole
    id_number: str | None = Field(default=None, pattern=r"^\d{9}$")
    phone_number: str | None = Field(default=None, max_length=20)
    affiliation: str | None = Field(default=None, max_length=255)

    @field_validator("affiliation")
    @classmethod
    def validate_affiliation(cls, value: str | None, info):
        role = info.data.get("role")
        if role == UserRole.EXTERNAL_REVIEWER and not value:
            raise ValueError("Affiliation is required for external reviewers")
        return value


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(TimestampedResponse):
    email: EmailStr
    full_name: str
    role: UserRole
    id_number: str | None
    phone_number: str | None
    affiliation: str | None
    is_active: bool
    is_approved: bool
    requires_manual_approval: bool


class CurrentUserResponse(APIModel):
    user: UserResponse


class UserSummary(APIModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: UserRole
