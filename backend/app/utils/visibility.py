from app.models.enums import ConferenceStatus, SessionStatus, UserRole


def can_view_conference(role: UserRole, status: ConferenceStatus) -> bool:
    if role == UserRole.ADMIN:
        return True
    return status == ConferenceStatus.ACTIVE


def can_view_session(role: UserRole, status: SessionStatus) -> bool:
    if role == UserRole.ADMIN:
        return True
    return status in {SessionStatus.UPCOMING, SessionStatus.ACTIVE}
