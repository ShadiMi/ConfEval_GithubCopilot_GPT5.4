from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.enums import FileAssetKind, FileAssetOwnerType
from app.models.project import FileAsset, Project
from app.models.user import User

ALLOWED_REVIEWER_CV_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}
MAX_REVIEWER_CV_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_PROJECT_ATTACHMENT_TYPES = {
    FileAssetKind.PROJECT_PAPER: {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    },
    FileAssetKind.PROJECT_SLIDES: {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    },
    FileAssetKind.PROJECT_ADDITIONAL: {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/zip": ".zip",
    },
}
MAX_PROJECT_ATTACHMENT_SIZE_BYTES = 50 * 1024 * 1024


class FileValidationError(ValueError):
    pass


class FileStorageService:
    def __init__(self, db: Session):
        self.db = db
        settings = get_settings()
        self.base_dir = Path(settings.local_upload_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _reviewer_cv_dir(self) -> Path:
        path = self.base_dir / "reviewer-cvs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    async def store_reviewer_cv(self, *, user: User, upload: UploadFile) -> FileAsset:
        extension = ALLOWED_REVIEWER_CV_TYPES.get(upload.content_type or "")
        if extension is None:
            raise FileValidationError("Reviewer CV must be a PDF, DOC, or DOCX file")

        content = await upload.read()
        if not content:
            raise FileValidationError("Reviewer CV file is required")
        if len(content) > MAX_REVIEWER_CV_SIZE_BYTES:
            raise FileValidationError("Reviewer CV must not exceed 10 MB")

        file_name = upload.filename or f"reviewer-cv{extension}"
        storage_key = f"reviewer-cvs/{user.id}/{uuid4()}{extension}"
        target_path = self.base_dir / storage_key
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)

        existing_asset = self.db.scalar(
            select(FileAsset)
            .where(FileAsset.user_id == user.id)
            .where(FileAsset.kind == FileAssetKind.REVIEWER_CV)
        )
        if existing_asset is not None:
            old_path = self.base_dir / existing_asset.storage_key
            if old_path.exists():
                old_path.unlink()
            existing_asset.file_name = file_name
            existing_asset.storage_key = storage_key
            existing_asset.content_type = upload.content_type or "application/octet-stream"
            existing_asset.size_bytes = len(content)
            existing_asset.metadata_json = {"purpose": "reviewer_cv"}
            return existing_asset

        asset = FileAsset(
            owner_type=FileAssetOwnerType.USER,
            kind=FileAssetKind.REVIEWER_CV,
            file_name=file_name,
            storage_key=storage_key,
            content_type=upload.content_type or "application/octet-stream",
            size_bytes=len(content),
            metadata_json={"purpose": "reviewer_cv"},
            owner_user=user,
        )
        self.db.add(asset)
        return asset

    def get_reviewer_cv_asset(self, user_id: UUID | str) -> FileAsset | None:
        return self.db.scalar(
            select(FileAsset)
            .where(FileAsset.user_id == UUID(str(user_id)))
            .where(FileAsset.kind == FileAssetKind.REVIEWER_CV)
        )

    def resolve_storage_path(self, asset: FileAsset) -> Path:
        return self.base_dir / asset.storage_key

    async def store_project_attachment(
        self,
        *,
        project: Project,
        upload: UploadFile,
        kind: FileAssetKind,
    ) -> FileAsset:
        allowed_types = ALLOWED_PROJECT_ATTACHMENT_TYPES.get(kind)
        if allowed_types is None:
            raise FileValidationError("Unsupported project attachment type")

        extension = allowed_types.get(upload.content_type or "")
        if extension is None:
            raise FileValidationError("Invalid attachment format for the selected project file type")

        content = await upload.read()
        if not content:
            raise FileValidationError("Project attachment file is required")
        if len(content) > MAX_PROJECT_ATTACHMENT_SIZE_BYTES:
            raise FileValidationError("Project attachment must not exceed 50 MB")

        file_name = upload.filename or f"attachment{extension}"
        storage_key = f"projects/{project.id}/{kind.value}-{uuid4()}{extension}"
        target_path = self.base_dir / storage_key
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)

        existing_asset = self.db.scalar(
            select(FileAsset)
            .where(FileAsset.project_id == project.id)
            .where(FileAsset.kind == kind)
        )
        if existing_asset is not None:
            old_path = self.base_dir / existing_asset.storage_key
            if old_path.exists():
                old_path.unlink()
            existing_asset.file_name = file_name
            existing_asset.storage_key = storage_key
            existing_asset.content_type = upload.content_type or "application/octet-stream"
            existing_asset.size_bytes = len(content)
            existing_asset.metadata_json = {"purpose": kind.value}
            return existing_asset

        asset = FileAsset(
            owner_type=FileAssetOwnerType.PROJECT,
            kind=kind,
            file_name=file_name,
            storage_key=storage_key,
            content_type=upload.content_type or "application/octet-stream",
            size_bytes=len(content),
            metadata_json={"purpose": kind.value},
            project=project,
        )
        self.db.add(asset)
        return asset

    def get_project_attachment(self, project_id: UUID | str, kind: FileAssetKind) -> FileAsset | None:
        return self.db.scalar(
            select(FileAsset)
            .where(FileAsset.project_id == UUID(str(project_id)))
            .where(FileAsset.kind == kind)
        )
