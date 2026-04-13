from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import project_reviewers, project_tags, project_team_members
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import FileAssetKind, FileAssetOwnerType, ProjectStatus, TeamInvitationStatus

if TYPE_CHECKING:
    from app.models.conference import Session
    from app.models.review import Review
    from app.models.tag import Tag
    from app.models.user import User


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text())
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus, native_enum=False), default=ProjectStatus.PENDING)
    mentor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    poster_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    edits_after_approval: Mapped[bool] = mapped_column(Boolean, default=False)

    owner: Mapped[User] = relationship(back_populates="owned_projects")
    session: Mapped[Session | None] = relationship(back_populates="projects")
    tags: Mapped[list[Tag]] = relationship(secondary=project_tags)
    team_members: Mapped[list[User]] = relationship(secondary=project_team_members, back_populates="team_projects")
    assigned_reviewers: Mapped[list[User]] = relationship(secondary=project_reviewers)
    attachments: Mapped[list[FileAsset]] = relationship(back_populates="project", cascade="all, delete-orphan")
    invitations: Mapped[list[TeamInvitation]] = relationship(back_populates="project", cascade="all, delete-orphan")
    reviews: Mapped[list[Review]] = relationship(back_populates="project", cascade="all, delete-orphan")


class FileAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "file_assets"

    owner_type: Mapped[FileAssetOwnerType] = mapped_column(Enum(FileAssetOwnerType, native_enum=False))
    kind: Mapped[FileAssetKind] = mapped_column(Enum(FileAssetKind, native_enum=False))
    file_name: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(512), unique=True)
    content_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column()
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)

    owner_user: Mapped[User | None] = relationship(back_populates="file_assets")
    project: Mapped[Project | None] = relationship(back_populates="attachments")


class TeamInvitation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "team_invitations"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[TeamInvitationStatus] = mapped_column(
        Enum(TeamInvitationStatus, native_enum=False),
        default=TeamInvitationStatus.PENDING,
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime]
    invited_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    project: Mapped[Project] = relationship(back_populates="invitations")
    invited_user: Mapped[User | None] = relationship(back_populates="invited_team_entries")
