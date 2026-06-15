import hashlib
import mimetypes
import uuid
from pathlib import PurePath

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import magic  # pip install python-magic

from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = settings.max_file_size  # 5MB

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    user = Depends(get_current_user),
):
    # 1. Ограничение размера
    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large (max 5MB)")

    # 2. Валидация MIME по содержимому (не по расширению!)
    mime = magic.from_buffer(content[:2048], mime=True)
    if mime not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, f"Unsupported file type: {mime}")

    # 3. Безопасное имя файла (без оригинального имени!)
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[mime]
    safe_name = f"{uuid.uuid4()}{ext}"

    # 4. Загрузка в MinIO...
    # minio_client.put_object(bucket, safe_name, content, len(content))

    return {"url": f"/uploads/{safe_name}"}