from app.models.enums import NotificationType
from app.schemas.common import APIModel, MessageResponse, TimestampedResponse


class NotificationResponse(TimestampedResponse):
    type: NotificationType
    title: str
    message: str
    link: str | None
    is_read: bool


class NotificationListResponse(APIModel):
    notifications: list[NotificationResponse]
    unread_count: int


class NotificationMarkAllResponse(MessageResponse):
    updated_count: int