from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.conference import Session as ConferenceSession
from app.models.enums import NotificationType, ReviewerApplicationStatus, SessionStatus, UserRole
from app.models.review import ReviewerApplication
from app.models.user import User
from app.services.notification_service import NotificationService


class ReviewerApplicationService:
    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    def _get_session(self, session_id: UUID | str) -> ConferenceSession:
        session = self.db.scalar(
            select(ConferenceSession)
            .where(ConferenceSession.id == UUID(str(session_id)))
            .options(selectinload(ConferenceSession.reviewers))
        )
        if session is None:
            raise ValueError("Session not found")
        return session

    def list_pending_applications(self) -> list[ReviewerApplication]:
        return list(
            self.db.scalars(
                select(ReviewerApplication)
                .where(ReviewerApplication.status == ReviewerApplicationStatus.PENDING)
                .options(selectinload(ReviewerApplication.reviewer), selectinload(ReviewerApplication.session))
                .order_by(ReviewerApplication.created_at.asc())
            )
        )

    def list_reviewer_applications(self, reviewer: User) -> list[ReviewerApplication]:
        return list(
            self.db.scalars(
                select(ReviewerApplication)
                .where(ReviewerApplication.reviewer_id == reviewer.id)
                .options(selectinload(ReviewerApplication.reviewer), selectinload(ReviewerApplication.session))
                .order_by(ReviewerApplication.created_at.desc())
            )
        )

    def apply_to_session(self, *, reviewer: User, session_id: UUID | str, cover_message: str | None) -> ReviewerApplication:
        if reviewer.role not in {UserRole.INTERNAL_REVIEWER, UserRole.EXTERNAL_REVIEWER}:
            raise PermissionError("Only reviewers can apply to sessions")

        session = self._get_session(session_id)
        if session.status == SessionStatus.COMPLETED:
            raise ValueError("Cannot apply to a completed session")
        if any(existing_reviewer.id == reviewer.id for existing_reviewer in session.reviewers):
            raise ValueError("Reviewer is already assigned to this session")

        existing_application = self.db.scalar(
            select(ReviewerApplication)
            .where(ReviewerApplication.reviewer_id == reviewer.id)
            .where(ReviewerApplication.session_id == session.id)
            .where(ReviewerApplication.status.in_([ReviewerApplicationStatus.PENDING, ReviewerApplicationStatus.APPROVED]))
        )
        if existing_application is not None:
            raise ValueError("A reviewer application already exists for this session")

        application = ReviewerApplication(
            reviewer=reviewer,
            session=session,
            status=ReviewerApplicationStatus.PENDING,
            cover_message=cover_message.strip() if cover_message else None,
        )
        self.db.add(application)
        self.notifications.create_notification(
            user=reviewer,
            notification_type=NotificationType.REVIEWER_APPLICATION_SUBMITTED,
            title="Session application submitted",
            message=f"Your application to review '{session.name}' has been submitted.",
            link="/dashboard/reviewer/sessions",
        )
        admins = list(self.db.scalars(select(User).where(User.role == UserRole.ADMIN).where(User.is_active.is_(True))))
        for admin in admins:
            self.notifications.create_notification(
                user=admin,
                notification_type=NotificationType.REVIEWER_APPLICATION_SUBMITTED,
                title="Reviewer application pending",
                message=f"{reviewer.full_name} applied to session '{session.name}'.",
                link="/dashboard/admin/applications",
            )
        self.db.commit()
        self.db.refresh(application)
        return self.get_application(application.id)

    def get_application(self, application_id: UUID | str) -> ReviewerApplication:
        application = self.db.scalar(
            select(ReviewerApplication)
            .where(ReviewerApplication.id == UUID(str(application_id)))
            .options(selectinload(ReviewerApplication.reviewer), selectinload(ReviewerApplication.session))
        )
        if application is None:
            raise ValueError("Reviewer application not found")
        return application

    def decide_application(
        self,
        *,
        actor: User,
        application_id: UUID | str,
        approved: bool,
        decision_notes: str | None,
    ) -> ReviewerApplication:
        if actor.role != UserRole.ADMIN:
            raise PermissionError("Only admins can decide reviewer applications")

        application = self.db.scalar(
            select(ReviewerApplication)
            .where(ReviewerApplication.id == UUID(str(application_id)))
            .options(
                selectinload(ReviewerApplication.reviewer),
                selectinload(ReviewerApplication.session).selectinload(ConferenceSession.reviewers),
            )
        )
        if application is None:
            raise ValueError("Reviewer application not found")
        if application.status != ReviewerApplicationStatus.PENDING:
            raise ValueError("Only pending applications can be decided")

        application.status = ReviewerApplicationStatus.APPROVED if approved else ReviewerApplicationStatus.REJECTED
        application.decision_notes = decision_notes.strip() if decision_notes else None
        application.decided_by_id = actor.id

        if approved and not any(user.id == application.reviewer_id for user in application.session.reviewers):
            application.session.reviewers.append(application.reviewer)
            self.notifications.create_notification(
                user=application.reviewer,
                notification_type=NotificationType.REVIEWER_ASSIGNED,
                title="Assigned to session",
                message=f"You have been assigned to review session '{application.session.name}'.",
                link="/dashboard/reviewer/sessions",
            )

        decision = "approved" if approved else "rejected"
        self.notifications.create_notification(
            user=application.reviewer,
            notification_type=NotificationType.REVIEWER_APPLICATION_DECISION,
            title=f"Session application {decision}",
            message=f"Your application for '{application.session.name}' was {decision}.",
            link="/dashboard/reviewer/sessions",
        )
        self.db.commit()
        self.db.refresh(application)
        return application
