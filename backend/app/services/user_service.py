from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import AuditEventType, UserRole
from app.models.notification import AuditLog
from app.models.user import User
from app.schemas.auth import PendingReviewerSummary
from app.schemas.user import UserSummary
from app.services.file_service import FileStorageService
from app.services.notification_service import NotificationService


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.files = FileStorageService(db)
        self.notifications = NotificationService(db)

    def list_pending_reviewers(self) -> list[User]:
        return list(
            self.db.scalars(
                select(User)
                .where(User.is_active.is_(True))
                .where(User.requires_manual_approval.is_(True))
                .where(User.is_approved.is_(False))
                .order_by(User.created_at.asc())
            )
        )

    def decide_reviewer(self, *, actor: User, user_id: UUID | str, approved: bool, reason: str | None) -> User:
        user = self.db.get(User, UUID(str(user_id)))
        if user is None or not user.is_reviewer:
            raise ValueError("Reviewer not found")
        if not user.is_active:
            raise ValueError("Reviewer is inactive")
        if user.is_approved == approved and approved:
            raise ValueError("Reviewer is already approved")

        user.is_approved = approved
        audit_event = AuditLog(
            actor=actor,
            event_type=AuditEventType.USER_APPROVED if approved else AuditEventType.USER_REJECTED,
            resource_type="user",
            resource_id=str(user.id),
            metadata_json={"reason": reason or ""},
        )
        self.db.add(audit_event)
        self.notifications.notify_reviewer_decision(user, approved=approved, reason=reason)
        self.db.commit()
        self.db.refresh(user)
        return user

    @staticmethod
    def summarize_pending_reviewers(users: list[User]) -> list[PendingReviewerSummary]:
        summaries: list[PendingReviewerSummary] = []
        for user in users:
            cv_asset = next((asset for asset in user.file_assets if asset.kind.value == "reviewer_cv"), None)
            summaries.append(
                PendingReviewerSummary(
                    id=user.id,
                    full_name=user.full_name,
                    email=user.email,
                    role=user.role.value,
                    affiliation=user.affiliation,
                    created_at=user.created_at,
                    cv_file_name=cv_asset.file_name if cv_asset else None,
                )
            )
        return summaries

    @staticmethod
    def summarize_users(users: list[User]) -> list[UserSummary]:
        return [UserSummary.model_validate(user) for user in users]
