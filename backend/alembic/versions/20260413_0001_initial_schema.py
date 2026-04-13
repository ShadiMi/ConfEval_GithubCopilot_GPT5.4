"""initial schema

Revision ID: 20260413_0001
Revises: None
Create Date: 2026-04-13 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260413_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conferences",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.Enum("draft", "active", "completed", "archived", name="conferencestatus", native_enum=False), nullable=False),
        sa.Column("location_label", sa.String(length=255), nullable=False),
        sa.Column("location_text", sa.Text(), nullable=True),
        sa.Column("location_building", sa.String(length=50), nullable=True),
        sa.Column("location_floor", sa.Integer(), nullable=True),
        sa.Column("location_room", sa.Integer(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("location_floor IS NULL OR location_floor IN (1, 2)", name="conference_floor_valid"),
        sa.PrimaryKeyConstraint("id", name="pk_conferences"),
    )
    op.create_index("ix_conferences_name", "conferences", ["name"], unique=False)
    op.create_index("ix_conferences_status", "conferences", ["status"], unique=False)

    op.create_table(
        "site_settings",
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("value_type", sa.String(length=32), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_site_settings"),
        sa.UniqueConstraint("key", name="uq_site_settings_key"),
    )
    op.create_index("ix_site_settings_key", "site_settings", ["key"], unique=False)

    op.create_table(
        "tags",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_tags"),
        sa.UniqueConstraint("name", name="uq_tags_name"),
    )
    op.create_index("ix_tags_name", "tags", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("id_number", sa.String(length=9), nullable=True),
        sa.Column("phone_number", sa.String(length=20), nullable=True),
        sa.Column("affiliation", sa.String(length=255), nullable=True),
        sa.Column("role", sa.Enum("student", "internal_reviewer", "external_reviewer", "admin", name="userrole", native_enum=False), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("requires_manual_approval", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("google_subject", sa.String(length=255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("google_subject", name="uq_users_google_subject"),
        sa.UniqueConstraint("id_number", name="uq_users_id_number"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.Enum(
            "user_approved",
            "user_rejected",
            "user_deactivated",
            "project_approved",
            "project_rejected",
            "project_updated",
            "review_submitted",
            "reviewer_assigned",
            "reviewer_auto_assigned",
            "report_exported",
            name="auditeventtype",
            native_enum=False,
        ), nullable=False),
        sa.Column("resource_type", sa.String(length=120), nullable=False),
        sa.Column("resource_id", sa.String(length=120), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], name="fk_audit_logs_actor_id_users", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )
    op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"], unique=False)

    op.create_table(
        "file_assets",
        sa.Column("owner_type", sa.Enum("user", "project", name="fileassetownertype", native_enum=False), nullable=False),
        sa.Column("kind", sa.Enum("reviewer_cv", "project_paper", "project_slides", "project_additional", name="fileassetkind", native_enum=False), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_file_assets_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_file_assets"),
        sa.UniqueConstraint("storage_key", name="uq_file_assets_storage_key"),
    )

    op.create_table(
        "notifications",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.Enum(
            "reviewer_registered",
            "reviewer_decision",
            "reviewer_assigned",
            "project_decision",
            "review_completed",
            "reviewer_application_submitted",
            "reviewer_application_decision",
            name="notificationtype",
            native_enum=False,
        ), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("link", sa.String(length=255), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_notifications_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_notifications"),
    )
    op.create_index("ix_notifications_type", "notifications", ["type"], unique=False)
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)

    op.create_table(
        "reviewer_interest_tags",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name="fk_reviewer_interest_tags_tag_id_tags", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_reviewer_interest_tags_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "tag_id", name="pk_reviewer_interest_tags"),
    )

    op.create_table(
        "sessions",
        sa.Column("conference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.Enum("upcoming", "active", "completed", name="sessionstatus", native_enum=False), nullable=False),
        sa.Column("location_label", sa.String(length=255), nullable=False),
        sa.Column("location_text", sa.Text(), nullable=True),
        sa.Column("max_project_capacity", sa.Integer(), nullable=False),
        sa.Column("reviewers_per_project", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conference_id"], ["conferences.id"], name="fk_sessions_conference_id_conferences", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_sessions"),
    )
    op.create_index("ix_sessions_name", "sessions", ["name"], unique=False)
    op.create_index("ix_sessions_status", "sessions", ["status"], unique=False)

    op.create_table(
        "criteria",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Numeric(5, 2), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("max_score >= 1 AND max_score <= 100", name="criteria_max_score_valid"),
        sa.CheckConstraint("weight >= 0.1 AND weight <= 10.0", name="criteria_weight_valid"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], name="fk_criteria_session_id_sessions", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_criteria"),
    )
    op.create_index("ix_criteria_session_id", "criteria", ["session_id"], unique=False)

    op.create_table(
        "projects",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("pending", "approved", "rejected", name="projectstatus", native_enum=False), nullable=False, server_default="pending"),
        sa.Column("mentor_email", sa.String(length=255), nullable=True),
        sa.Column("poster_number", sa.String(length=50), nullable=True),
        sa.Column("edits_after_approval", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name="fk_projects_owner_id_users", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], name="fk_projects_session_id_sessions", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"], unique=False)
    op.create_index("ix_projects_title", "projects", ["title"], unique=False)

    op.create_table(
        "project_reviewers",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_project_reviewers_project_id_projects", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_project_reviewers_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "user_id", name="pk_project_reviewers"),
    )

    op.create_table(
        "project_tags",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_project_tags_project_id_projects", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name="fk_project_tags_tag_id_tags", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "tag_id", name="pk_project_tags"),
    )

    op.create_table(
        "project_team_members",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_project_team_members_project_id_projects", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_project_team_members_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "user_id", name="pk_project_team_members"),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_team_member"),
    )

    op.create_table(
        "review_assignment_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_review_assignment_snapshots_project_id_projects", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_review_assignment_snapshots_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_review_assignment_snapshots"),
    )

    op.create_table(
        "reviewer_applications",
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.Enum("pending", "approved", "rejected", name="reviewerapplicationstatus", native_enum=False), nullable=False, server_default="pending"),
        sa.Column("cover_message", sa.Text(), nullable=True),
        sa.Column("decision_notes", sa.Text(), nullable=True),
        sa.Column("decided_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["decided_by_id"], ["users.id"], name="fk_reviewer_applications_decided_by_id_users", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], name="fk_reviewer_applications_reviewer_id_users", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], name="fk_reviewer_applications_session_id_sessions", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_reviewer_applications"),
    )
    op.create_index("ix_reviewer_applications_reviewer_id", "reviewer_applications", ["reviewer_id"], unique=False)
    op.create_index("ix_reviewer_applications_session_id", "reviewer_applications", ["session_id"], unique=False)

    op.create_table(
        "session_reviewers",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], name="fk_session_reviewers_session_id_sessions", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_session_reviewers_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("session_id", "user_id", name="pk_session_reviewers"),
    )

    op.create_table(
        "session_tags",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], name="fk_session_tags_session_id_sessions", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name="fk_session_tags_tag_id_tags", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("session_id", "tag_id", name="pk_session_tags"),
    )

    op.create_table(
        "team_invitations",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Enum("pending", "accepted", "declined", name="teaminvitationstatus", native_enum=False), nullable=False, server_default="pending"),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("invited_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["invited_user_id"], ["users.id"], name="fk_team_invitations_invited_user_id_users", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_team_invitations_project_id_projects", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_team_invitations"),
        sa.UniqueConstraint("token", name="uq_team_invitations_token"),
    )
    op.create_index("ix_team_invitations_email", "team_invitations", ["email"], unique=False)
    op.create_index("ix_team_invitations_project_id", "team_invitations", ["project_id"], unique=False)
    op.create_index("ix_team_invitations_token", "team_invitations", ["token"], unique=False)

    op.create_foreign_key(
        "fk_file_assets_project_id_projects",
        "file_assets",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_table(
        "reviews",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.Enum("draft", "submitted", name="reviewstatus", native_enum=False), nullable=False, server_default="draft"),
        sa.Column("overall_comment", sa.Text(), nullable=True),
        sa.Column("total_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_reviews_project_id_projects", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], name="fk_reviews_reviewer_id_users", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], name="fk_reviews_session_id_sessions", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_reviews"),
        sa.UniqueConstraint("project_id", "reviewer_id", name="uq_project_reviewer_review"),
    )
    op.create_index("ix_reviews_project_id", "reviews", ["project_id"], unique=False)
    op.create_index("ix_reviews_reviewer_id", "reviews", ["reviewer_id"], unique=False)
    op.create_index("ix_reviews_session_id", "reviews", ["session_id"], unique=False)

    op.create_table(
        "review_criterion_scores",
        sa.Column("review_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("criteria_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Numeric(6, 2), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("score >= 0", name="review_score_non_negative"),
        sa.ForeignKeyConstraint(["criteria_id"], ["criteria.id"], name="fk_review_criterion_scores_criteria_id_criteria", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], name="fk_review_criterion_scores_review_id_reviews", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_review_criterion_scores"),
    )
    op.create_index("ix_review_criterion_scores_criteria_id", "review_criterion_scores", ["criteria_id"], unique=False)
    op.create_index("ix_review_criterion_scores_review_id", "review_criterion_scores", ["review_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_review_criterion_scores_review_id", table_name="review_criterion_scores")
    op.drop_index("ix_review_criterion_scores_criteria_id", table_name="review_criterion_scores")
    op.drop_table("review_criterion_scores")

    op.drop_index("ix_reviews_session_id", table_name="reviews")
    op.drop_index("ix_reviews_reviewer_id", table_name="reviews")
    op.drop_index("ix_reviews_project_id", table_name="reviews")
    op.drop_table("reviews")

    op.drop_constraint("fk_file_assets_project_id_projects", "file_assets", type_="foreignkey")

    op.drop_index("ix_team_invitations_token", table_name="team_invitations")
    op.drop_index("ix_team_invitations_project_id", table_name="team_invitations")
    op.drop_index("ix_team_invitations_email", table_name="team_invitations")
    op.drop_table("team_invitations")

    op.drop_table("session_tags")
    op.drop_table("session_reviewers")

    op.drop_index("ix_reviewer_applications_session_id", table_name="reviewer_applications")
    op.drop_index("ix_reviewer_applications_reviewer_id", table_name="reviewer_applications")
    op.drop_table("reviewer_applications")

    op.drop_table("review_assignment_snapshots")
    op.drop_table("project_team_members")
    op.drop_table("project_tags")
    op.drop_table("project_reviewers")

    op.drop_index("ix_projects_title", table_name="projects")
    op.drop_index("ix_projects_owner_id", table_name="projects")
    op.drop_table("projects")

    op.drop_index("ix_criteria_session_id", table_name="criteria")
    op.drop_table("criteria")

    op.drop_index("ix_sessions_status", table_name="sessions")
    op.drop_index("ix_sessions_name", table_name="sessions")
    op.drop_table("sessions")

    op.drop_table("reviewer_interest_tags")

    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("ix_notifications_type", table_name="notifications")
    op.drop_table("notifications")

    op.drop_table("file_assets")

    op.drop_index("ix_audit_logs_event_type", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_tags_name", table_name="tags")
    op.drop_table("tags")

    op.drop_index("ix_site_settings_key", table_name="site_settings")
    op.drop_table("site_settings")

    op.drop_index("ix_conferences_status", table_name="conferences")
    op.drop_index("ix_conferences_name", table_name="conferences")
    op.drop_table("conferences")
