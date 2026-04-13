from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.models.base import Base

session_tags = Table(
    "session_tags",
    Base.metadata,
    Column("session_id", PGUUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", PGUUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

project_tags = Table(
    "project_tags",
    Base.metadata,
    Column("project_id", PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", PGUUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

reviewer_interest_tags = Table(
    "reviewer_interest_tags",
    Base.metadata,
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", PGUUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

project_team_members = Table(
    "project_team_members",
    Base.metadata,
    Column("project_id", PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("project_id", "user_id", name="uq_project_team_member"),
)

session_reviewers = Table(
    "session_reviewers",
    Base.metadata,
    Column("session_id", PGUUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

project_reviewers = Table(
    "project_reviewers",
    Base.metadata,
    Column("project_id", PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

review_assignment_snapshots = Table(
    "review_assignment_snapshots",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("project_id", PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
)
