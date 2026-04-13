from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import project_team_members, reviewer_interest_tags
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.conference import Session
    from app.models.notification import AuditLog, Notification
    from app.models.project import FileAsset, Project, TeamInvitation
    from app.models.review import Review, ReviewerApplication
    from app.models.tag import Tag


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    id_number: Mapped[str | None] = mapped_column(String(9), unique=True, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    affiliation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_manual_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    google_subject: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text(), nullable=True)

    reviewer_interest_tags: Mapped[list[Tag]] = relationship(secondary=reviewer_interest_tags)
    owned_projects: Mapped[list[Project]] = relationship(back_populates="owner")
    team_projects: Mapped[list[Project]] = relationship(secondary=project_team_members, back_populates="team_members")
    file_assets: Mapped[list[FileAsset]] = relationship(back_populates="owner_user")
    submitted_reviews: Mapped[list[Review]] = relationship(back_populates="reviewer")
    reviewer_applications: Mapped[list[ReviewerApplication]] = relationship(
        back_populates="reviewer",
        foreign_keys="ReviewerApplication.reviewer_id",
    )
    notifications: Mapped[list[Notification]] = relationship(back_populates="user")
    audit_events: Mapped[list[AuditLog]] = relationship(back_populates="actor")
    invited_team_entries: Mapped[list[TeamInvitation]] = relationship(back_populates="invited_user")

    @property
    def is_reviewer(self) -> bool:
        return self.role in {UserRole.INTERNAL_REVIEWER, UserRole.EXTERNAL_REVIEWER}
