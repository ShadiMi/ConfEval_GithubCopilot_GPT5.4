from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.enums import FileAssetKind, FileAssetOwnerType, UserRole
from app.models.project import Project
from app.models.user import User
from app.services.file_service import FileStorageService, FileValidationError


class DummyUploadFile:
    def __init__(self, *, filename: str, content_type: str, content: bytes):
        self.filename = filename
        self.content_type = content_type
        self._content = content

    async def read(self) -> bytes:
        return self._content


@pytest.mark.asyncio
async def test_store_reviewer_cv_writes_file_and_adds_metadata(tmp_path: Path) -> None:
    db = Mock()
    db.scalar.return_value = None
    service = FileStorageService(db)
    service.base_dir = tmp_path

    user = User(
        id=uuid4(),
        email="reviewer@example.com",
        full_name="Reviewer Example",
        role=UserRole.EXTERNAL_REVIEWER,
        is_active=True,
        is_approved=False,
        requires_manual_approval=True,
    )
    upload = DummyUploadFile(filename="cv.pdf", content_type="application/pdf", content=b"pdf-content")

    asset = await service.store_reviewer_cv(user=user, upload=upload)

    assert asset.kind == FileAssetKind.REVIEWER_CV
    assert asset.owner_type == FileAssetOwnerType.USER
    assert (tmp_path / asset.storage_key).read_bytes() == b"pdf-content"
    db.add.assert_called_once_with(asset)


@pytest.mark.asyncio
async def test_store_reviewer_cv_rejects_invalid_content_type(tmp_path: Path) -> None:
    db = Mock()
    db.scalar.return_value = None
    service = FileStorageService(db)
    service.base_dir = tmp_path

    user = User(
        id=uuid4(),
        email="reviewer@example.com",
        full_name="Reviewer Example",
        role=UserRole.EXTERNAL_REVIEWER,
        is_active=True,
        is_approved=False,
        requires_manual_approval=True,
    )
    upload = DummyUploadFile(filename="cv.txt", content_type="text/plain", content=b"notes")

    with pytest.raises(FileValidationError, match="PDF, DOC, or DOCX"):
        await service.store_reviewer_cv(user=user, upload=upload)


@pytest.mark.asyncio
async def test_store_project_attachment_writes_project_file(tmp_path: Path) -> None:
    db = Mock()
    db.scalar.return_value = None
    service = FileStorageService(db)
    service.base_dir = tmp_path

    owner = User(
        id=uuid4(),
        email="student@example.com",
        full_name="Student Example",
        role=UserRole.STUDENT,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )
    project = Project(
        id=uuid4(),
        title="Poster Project",
        description="Description",
        owner=owner,
    )
    upload = DummyUploadFile(
        filename="paper.pdf",
        content_type="application/pdf",
        content=b"project-paper",
    )

    asset = await service.store_project_attachment(
        project=project,
        upload=upload,
        kind=FileAssetKind.PROJECT_PAPER,
    )

    assert asset.kind == FileAssetKind.PROJECT_PAPER
    assert asset.owner_type == FileAssetOwnerType.PROJECT
    assert (tmp_path / asset.storage_key).read_bytes() == b"project-paper"


@pytest.mark.asyncio
async def test_store_project_attachment_rejects_invalid_type(tmp_path: Path) -> None:
    db = Mock()
    db.scalar.return_value = None
    service = FileStorageService(db)
    service.base_dir = tmp_path

    owner = User(
        id=uuid4(),
        email="student@example.com",
        full_name="Student Example",
        role=UserRole.STUDENT,
        is_active=True,
        is_approved=True,
        requires_manual_approval=False,
    )
    project = Project(
        id=uuid4(),
        title="Poster Project",
        description="Description",
        owner=owner,
    )
    upload = DummyUploadFile(filename="slides.txt", content_type="text/plain", content=b"bad")

    with pytest.raises(FileValidationError, match="Invalid attachment format"):
        await service.store_project_attachment(
            project=project,
            upload=upload,
            kind=FileAssetKind.PROJECT_SLIDES,
        )
