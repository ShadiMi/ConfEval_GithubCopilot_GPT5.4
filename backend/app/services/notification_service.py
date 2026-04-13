from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import NotificationType, UserRole
from app.models.notification import Notification
from app.models.user import User


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        *,
        user: User,
        notification_type: NotificationType,
        title: str,
        message: str,
        link: str | None = None,
    ) -> Notification:
        notification = Notification(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            link=link,
        )
        self.db.add(notification)
        return notification

    def list_notifications(self, user: User) -> list[Notification]:
        return list(
            self.db.scalars(
                select(Notification)
                .where(Notification.user_id == user.id)
                .order_by(Notification.is_read.asc(), Notification.created_at.desc())
            )
        )

    def get_unread_count(self, user: User) -> int:
        return int(
            self.db.scalar(
                select(func.count(Notification.id))
                .where(Notification.user_id == user.id)
                .where(Notification.is_read.is_(False))
            )
            or 0
        )

    def mark_as_read(self, *, user: User, notification_id: UUID | str) -> Notification:
        notification = self.db.scalar(
            select(Notification)
            .where(Notification.id == UUID(str(notification_id)))
            .where(Notification.user_id == user.id)
        )
        if notification is None:
            raise ValueError("Notification not found")

        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, user: User) -> int:
        notifications = list(
            self.db.scalars(
                select(Notification)
                .where(Notification.user_id == user.id)
                .where(Notification.is_read.is_(False))
            )
        )
        for notification in notifications:
            notification.is_read = True
        self.db.commit()
        return len(notifications)

    def notify_admins_of_pending_reviewer(self, reviewer: User) -> None:
        admins = list(
            self.db.scalars(
                select(User)
                .where(User.role == UserRole.ADMIN)
                .where(User.is_active.is_(True))
            )
        )
        for admin in admins:
            self.create_notification(
                user=admin,
                notification_type=NotificationType.REVIEWER_REGISTERED,
                title="Reviewer approval required",
                message=f"{reviewer.full_name} is waiting for reviewer approval.",
                link=f"/admin/users/{reviewer.id}",
            )

    def notify_reviewer_decision(self, reviewer: User, approved: bool, reason: str | None = None) -> None:
        decision = "approved" if approved else "rejected"
        reason_suffix = f" Reason: {reason}" if reason else ""
        self.create_notification(
            user=reviewer,
            notification_type=NotificationType.REVIEWER_DECISION,
            title=f"Reviewer account {decision}",
            message=f"Your reviewer account has been {decision}.{reason_suffix}",
            link="/login" if approved else None,
        )
