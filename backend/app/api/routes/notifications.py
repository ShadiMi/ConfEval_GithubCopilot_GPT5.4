from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.notification import NotificationListResponse, NotificationMarkAllResponse, NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
def list_my_notifications(db: DbSession, current_user: CurrentUser) -> NotificationListResponse:
    service = NotificationService(db)
    notifications = service.list_notifications(current_user)
    unread_count = service.get_unread_count(current_user)
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(notification) for notification in notifications],
        unread_count=unread_count,
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(notification_id: str, db: DbSession, current_user: CurrentUser) -> NotificationResponse:
    service = NotificationService(db)
    try:
        notification = service.mark_as_read(user=current_user, notification_id=notification_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return NotificationResponse.model_validate(notification)


@router.post("/read-all", response_model=NotificationMarkAllResponse)
def mark_all_notifications_as_read(db: DbSession, current_user: CurrentUser) -> NotificationMarkAllResponse:
    service = NotificationService(db)
    updated_count = service.mark_all_as_read(current_user)
    return NotificationMarkAllResponse(message="Notifications marked as read", updated_count=updated_count)