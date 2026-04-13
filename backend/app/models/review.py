from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReviewStatus, ReviewerApplicationStatus

if TYPE_CHECKING:
    from app.models.conference import Criteria, Session
    from app.models.project import Project
    from app.models.user import User


class Review(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reviews"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    reviewer_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus, native_enum=False), default=ReviewStatus.DRAFT)
    overall_comment: Mapped[str | None] = mapped_column(Text(), nullable=True)
    total_score: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)

    project: Mapped[Project] = relationship(back_populates="reviews")
    reviewer: Mapped[User] = relationship(back_populates="submitted_reviews")
    criterion_scores: Mapped[list[ReviewCriterionScore]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )

    __table_args__ = (UniqueConstraint("project_id", "reviewer_id", name="uq_project_reviewer_review"),)


class ReviewCriterionScore(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "review_criterion_scores"

    review_id: Mapped[str] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True)
    criteria_id: Mapped[str] = mapped_column(ForeignKey("criteria.id", ondelete="CASCADE"), index=True)
    score: Mapped[float] = mapped_column(Numeric(6, 2))

    review: Mapped[Review] = relationship(back_populates="criterion_scores")
    criteria: Mapped[Criteria] = relationship()

    __table_args__ = (CheckConstraint("score >= 0", name="review_score_non_negative"),)


class ReviewerApplication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reviewer_applications"

    reviewer_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    status: Mapped[ReviewerApplicationStatus] = mapped_column(
        Enum(ReviewerApplicationStatus, native_enum=False),
        default=ReviewerApplicationStatus.PENDING,
    )
    cover_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    decision_notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    decided_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    reviewer: Mapped[User] = relationship(foreign_keys=[reviewer_id], back_populates="reviewer_applications")
    session: Mapped[Session] = relationship(back_populates="reviewer_applications")

    @property
    def session_name(self) -> str:
        return self.session.name

    @property
    def session_status(self):
        return self.session.status
