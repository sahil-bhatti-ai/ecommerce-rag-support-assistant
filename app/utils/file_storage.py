import re
from pathlib import Path
from uuid import UUID

import aiofiles
from fastapi import UploadFile

from app.core.config import get_settings

ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".pdf"}


def validate_upload_extension(extension: str) -> bool:
    return extension.lower() in ALLOWED_EXTENSIONS


def safe_filename(filename: str) -> str:
    filename = Path(filename).name
    filename = re.sub(r"[^a-zA-Z0-9._-]+", "_", filename)
    return filename[:180]


async def save_upload_file(file: UploadFile, document_id: UUID) -> Path:
    settings = get_settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{document_id}_{safe_filename(file.filename or 'upload.txt')}"
    path = settings.upload_dir / filename

    async with aiofiles.open(path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            await out_file.write(chunk)

    return path
