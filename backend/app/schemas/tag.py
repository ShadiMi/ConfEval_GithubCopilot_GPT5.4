from pydantic import BaseModel, Field

from app.schemas.common import APIModel, TimestampedResponse


class TagCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)


class TagResponse(TimestampedResponse):
    name: str
    description: str | None


class TagListResponse(APIModel):
    tags: list[TagResponse]
