from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(APIModel):
    message: str


class TokenPair(APIModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TimestampedResponse(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
