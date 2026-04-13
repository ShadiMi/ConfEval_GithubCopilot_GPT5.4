from app.models.enums import ConferenceStatus, SessionStatus, UserRole
from app.utils.visibility import can_view_conference, can_view_session


def test_non_admin_can_only_view_active_conferences() -> None:
    assert can_view_conference(UserRole.STUDENT, ConferenceStatus.ACTIVE) is True
    assert can_view_conference(UserRole.STUDENT, ConferenceStatus.DRAFT) is False


def test_admin_can_view_all_conferences() -> None:
    assert can_view_conference(UserRole.ADMIN, ConferenceStatus.DRAFT) is True
    assert can_view_conference(UserRole.ADMIN, ConferenceStatus.ARCHIVED) is True


def test_non_admin_can_only_view_upcoming_and_active_sessions() -> None:
    assert can_view_session(UserRole.EXTERNAL_REVIEWER, SessionStatus.UPCOMING) is True
    assert can_view_session(UserRole.EXTERNAL_REVIEWER, SessionStatus.ACTIVE) is True
    assert can_view_session(UserRole.EXTERNAL_REVIEWER, SessionStatus.COMPLETED) is False
