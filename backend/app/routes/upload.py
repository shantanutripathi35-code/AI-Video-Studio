from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
MAX_SIZE = 500 * 1024 * 1024  # 500 MB


@router.post("/video")
async def upload_video(file: UploadFile = File(...)):
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format."
        )

    video_id = str(uuid4())
    save_path = UPLOAD_DIR / f"{video_id}{extension}"

    size = 0

    with open(save_path, "wb") as output:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)

            if size > MAX_SIZE:
                output.close()
                save_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail="Video exceeds maximum size."
                )

            output.write(chunk)

    return {
        "video_id": video_id,
        "filename": file.filename,
        "size": size,
        "path": str(save_path),
        "status": "uploaded"
    }
