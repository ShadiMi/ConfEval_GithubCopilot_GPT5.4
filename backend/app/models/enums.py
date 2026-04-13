from enum import StrEnum


class UserRole(StrEnum):
    STUDENT = "student"
    INTERNAL_REVIEWER = "internal_reviewer"
    EXTERNAL_REVIEWER = "external_reviewer"
    ADMIN = "admin"


class ConferenceStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class SessionStatus(StrEnum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"


class ProjectStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


class ReviewerApplicationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class NotificationType(StrEnum):
    REVIEWER_REGISTERED = "reviewer_registered"
    REVIEWER_DECISION = "reviewer_decision"
    REVIEWER_ASSIGNED = "reviewer_assigned"
    PROJECT_DECISION = "project_decision"
    REVIEW_COMPLETED = "review_completed"
    REVIEWER_APPLICATION_SUBMITTED = "reviewer_application_submitted"
    REVIEWER_APPLICATION_DECISION = "reviewer_application_decision"


class TeamInvitationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class FileAssetKind(StrEnum):
    REVIEWER_CV = "reviewer_cv"
    PROJECT_PAPER = "project_paper"
    PROJECT_SLIDES = "project_slides"
    PROJECT_ADDITIONAL = "project_additional"


class FileAssetOwnerType(StrEnum):
    USER = "user"
    PROJECT = "project"


class AuditEventType(StrEnum):
    USER_APPROVED = "user_approved"
    USER_REJECTED = "user_rejected"
    USER_DEACTIVATED = "user_deactivated"
    PROJECT_APPROVED = "project_approved"
    PROJECT_REJECTED = "project_rejected"
    PROJECT_UPDATED = "project_updated"
    REVIEW_SUBMITTED = "review_submitted"
    REVIEWER_ASSIGNED = "reviewer_assigned"
    REVIEWER_AUTO_ASSIGNED = "reviewer_auto_assigned"
    REPORT_EXPORTED = "report_exported"
