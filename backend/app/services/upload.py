import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = settings.max_file_size  # 5MB

@router.post("/product-image")
async def upload_product_image(
    file: UploadFile = File(...),
    user = Depends(get_current_user),
) -> dict:
    # ✅ Проверка MIME-типа
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"Неподдерживаемый тип: {file.content_type}")
    
    # ✅ Проверка расширения
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Неподдерживаемое расширение: {ext}")
    
    # ✅ Чтение с ограничением размера
    data = await file.read(MAX_FILE_SIZE + 1)
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(413, f"Файл превышает {MAX_FILE_SIZE // 1024 // 1024}MB")
    
    # ✅ UUID-имя (не оригинальное имя файла!)
    safe_name = f"{uuid.uuid4()}{ext}"
    
    # TODO: загрузить в MinIO под safe_name
    return {"filename": safe_name, "size": len(data)}