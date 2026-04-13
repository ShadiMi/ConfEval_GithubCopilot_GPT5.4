from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    TokenPayloadError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import TokenPair
from app.schemas.user import UserLoginRequest, UserRegisterRequest
from app.services.file_service import FileStorageService
from app.services.notification_service import NotificationService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.files = FileStorageService(db)
        self.notifications = NotificationService(db)

    def _ensure_email_is_available(self, email: str) -> None:
        existing_user = self.db.scalar(select(User).where(User.email == email))
        if existing_user is not None:
            raise ValueError("Email is already registered")

    def _build_user(self, payload: UserRegisterRequest) -> User:
        requires_manual_approval = payload.role in {
            UserRole.INTERNAL_REVIEWER,
            UserRole.EXTERNAL_REVIEWER,
        }
        return User(
            email=str(payload.email).lower(),
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            role=payload.role,
            id_number=payload.id_number,
            phone_number=payload.phone_number,
            affiliation=payload.affiliation,
            requires_manual_approval=requires_manual_approval,
            is_approved=payload.role == UserRole.STUDENT,
        )

    def register_user(self, payload: UserRegisterRequest) -> User:
        normalized_email = str(payload.email).lower()
        self._ensure_email_is_available(normalized_email)

        user = self._build_user(payload)
        self.db.add(user)
        if user.requires_manual_approval:
            self.notifications.notify_admins_of_pending_reviewer(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def register_external_reviewer(self, payload: UserRegisterRequest, cv_upload: UploadFile) -> User:
        if payload.role != UserRole.EXTERNAL_REVIEWER:
            raise ValueError("External reviewer registration requires the external reviewer role")

        normalized_email = str(payload.email).lower()
        self._ensure_email_is_available(normalized_email)

        user = self._build_user(payload)
        self.db.add(user)
        self.db.flush()

        try:
            await self.files.store_reviewer_cv(user=user, upload=cv_upload)
            self.notifications.notify_admins_of_pending_reviewer(user)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(user)
        return user

    def login_user(self, payload: UserLoginRequest) -> TokenPair:
        user = self.db.scalar(select(User).where(User.email == str(payload.email).lower()))
        if user is None or user.password_hash is None:
            raise ValueError("Invalid credentials")
        if not verify_password(payload.password, user.password_hash):
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise PermissionError("User is inactive")
        if user.requires_manual_approval and not user.is_approved:
            raise PermissionError("User is pending approval")

        return TokenPair(
            access_token=create_access_token(str(user.id), user.role.value),
            refresh_token=create_refresh_token(str(user.id), user.role.value),
        )

    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except TokenPayloadError as exc:
            raise ValueError("Invalid refresh token") from exc

        user = self.db.scalar(select(User).where(User.id == payload["sub"]))
        if user is None:
            raise ValueError("Invalid refresh token")
        if not user.is_active:
            raise PermissionError("User is inactive")
        if user.requires_manual_approval and not user.is_approved:
            raise PermissionError("User is pending approval")

        return TokenPair(
            access_token=create_access_token(str(user.id), user.role.value),
            refresh_token=create_refresh_token(str(user.id), user.role.value),
        )
