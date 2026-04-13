from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import session_reviewers, session_tags
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ConferenceStatus, SessionStatus

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.review import ReviewerApplication
    from app.models.tag import Tag
    from app.models.user import User


class Conference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "conferences"

    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    start_date: Mapped[Date] = mapped_column(Date())
    end_date: Mapped[Date] = mapped_column(Date())
    status: Mapped[ConferenceStatus] = mapped_column(Enum(ConferenceStatus, native_enum=False), index=True)
    location_label: Mapped[str] = mapped_column(String(255))
    location_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    location_building: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location_floor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location_room: Mapped[int | None] = mapped_column(Integer, nullable=True)

    sessions: Mapped[list[Session]] = relationship(back_populates="conference", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("location_floor IS NULL OR location_floor IN (1, 2)", name="conference_floor_valid"),
    )


class Session(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    conference_id: Mapped[str | None] = mapped_column(ForeignKey("conferences.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    start_date: Mapped[Date] = mapped_column(Date())
    end_date: Mapped[Date] = mapped_column(Date())
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus, native_enum=False), index=True)
    location_label: Mapped[str] = mapped_column(String(255))
    location_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    max_project_capacity: Mapped[int] = mapped_column(Integer)
    reviewers_per_project: Mapped[int] = mapped_column(Integer, default=2)

    conference: Mapped[Conference | None] = relationship(back_populates="sessions")
    criteria: Mapped[list[Criteria]] = relationship(back_populates="session", cascade="all, delete-orphan")
    tags: Mapped[list[Tag]] = relationship(secondary=session_tags)
    reviewers: Mapped[list[User]] = relationship(secondary=session_reviewers)
    projects: Mapped[list[Project]] = relationship(back_populates="session")
    reviewer_applications: Mapped[list[ReviewerApplication]] = relationship(back_populates="session")


class Criteria(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "criteria"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    max_score: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Numeric(5, 2))
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped[Session] = relationship(back_populates="criteria")

    __table_args__ = (
        CheckConstraint("max_score >= 1 AND max_score <= 100", name="criteria_max_score_valid"),
        CheckConstraint("weight >= 0.1 AND weight <= 10.0", name="criteria_weight_valid"),
    )
