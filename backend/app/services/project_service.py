from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import AuditEventType, FileAssetKind, NotificationType, ProjectStatus, UserRole
from app.models.notification import AuditLog
from app.models.project import Project
from app.models.user import User
from app.services.file_service import FileStorageService
from app.services.notification_service import NotificationService


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.files = FileStorageService(db)
        self.notifications = NotificationService(db)

    async def create_project(
        self,
        *,
        owner: User,
        title: str,
        description: str,
        mentor_email: str | None,
        session_id: str | None,
        paper_upload,
        slides_upload,
        additional_upload,
    ) -> Project:
        if owner.role not in {UserRole.STUDENT, UserRole.ADMIN}:
            raise PermissionError("Only students or admins can create projects")

        project = Project(
            owner=owner,
            title=title.strip(),
            description=description.strip(),
            mentor_email=mentor_email,
            session_id=UUID(session_id) if session_id else None,
            status=ProjectStatus.PENDING,
        )
        self.db.add(project)
        self.db.flush()

        try:
            if paper_upload is not None:
                await self.files.store_project_attachment(
                    project=project,
                    upload=paper_upload,
                    kind=FileAssetKind.PROJECT_PAPER,
                )
            if slides_upload is not None:
                await self.files.store_project_attachment(
                    project=project,
                    upload=slides_upload,
                    kind=FileAssetKind.PROJECT_SLIDES,
                )
            if additional_upload is not None:
                await self.files.store_project_attachment(
                    project=project,
                    upload=additional_upload,
                    kind=FileAssetKind.PROJECT_ADDITIONAL,
                )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(project)
        return self.get_project(project.id)

    def get_project(self, project_id: UUID | str) -> Project:
        project = self.db.scalar(
            select(Project)
            .where(Project.id == UUID(str(project_id)))
            .options(
                selectinload(Project.owner),
                selectinload(Project.attachments),
                selectinload(Project.team_members),
                selectinload(Project.invitations),
            )
        )
        if project is None:
            raise ValueError("Project not found")
        return project

    def list_owned_projects(self, owner: User) -> list[Project]:
        return list(
            self.db.scalars(
                select(Project)
                .where(Project.owner_id == owner.id)
                .options(
                    selectinload(Project.owner),
                    selectinload(Project.attachments),
                    selectinload(Project.team_members),
                    selectinload(Project.invitations),
                )
                .order_by(Project.created_at.desc())
            )
        )

    def list_pending_projects(self) -> list[Project]:
        return list(
            self.db.scalars(
                select(Project)
                .where(Project.status == ProjectStatus.PENDING)
                .options(
                    selectinload(Project.owner),
                    selectinload(Project.attachments),
                    selectinload(Project.team_members),
                    selectinload(Project.invitations),
                )
                .order_by(Project.created_at.asc())
            )
        )

    def decide_project(
        self,
        *,
        actor: User,
        project_id: UUID | str,
        approved: bool,
        poster_number: str | None,
        reason: str | None,
    ) -> Project:
        project = self.get_project(project_id)
        if actor.role != UserRole.ADMIN:
            raise PermissionError("Only admins can decide project status")

        project.status = ProjectStatus.APPROVED if approved else ProjectStatus.REJECTED
        if approved and poster_number:
            project.poster_number = poster_number.strip()

        self.db.add(
            AuditLog(
                actor=actor,
                event_type=AuditEventType.PROJECT_APPROVED if approved else AuditEventType.PROJECT_REJECTED,
                resource_type="project",
                resource_id=str(project.id),
                metadata_json={"reason": reason or "", "poster_number": project.poster_number or ""},
            )
        )
        decision = "approved" if approved else "rejected"
        message = f"Your project '{project.title}' has been {decision}."
        if reason:
            message = f"{message} Reason: {reason}"
        self.notifications.create_notification(
            user=project.owner,
            notification_type=NotificationType.PROJECT_DECISION,
            title=f"Project {decision}",
            message=message,
            link="/dashboard/student/projects",
        )
        self.db.commit()
        self.db.refresh(project)
        return self.get_project(project.id)
