from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
from uuid import uuid4
from app.services.smart_cut import SmartCutService

router = APIRouter(prefix="/smartcut", tags=["Smart Cut"])

UPLOAD_DIR = Path("storage/uploads")
OUTPUT_DIR = Path("storage/outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
MAX_SIZE = 500 * 1024 * 1024  # 500 MB

smart_cut_service = SmartCutService(str(OUTPUT_DIR))


@router.post("/process")
async def process_smart_cut(file: UploadFile = File(...)):
    """
    Smart Cut video editing pipeline:
    1. Upload Video
    2. Detect Silence
    3. Build Edit Timeline
    4. Render Video
    5. Save Output
    
    Returns JSON with output video path and processing stats
    """
    
    # Validate file extension
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format."
        )

    # Generate unique ID
    project_id = str(uuid4())
    video_path = UPLOAD_DIR / f"smartcut_{project_id}{extension}"

    # Upload video with chunking
    size = 0
    try:
        with open(video_path, "wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)

                if size > MAX_SIZE:
                    output.close()
                    video_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail="Video exceeds maximum size."
                    )

                output.write(chunk)

        # Process video with SmartCut
        result = smart_cut_service.process_smart_cut(str(video_path))

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Smart Cut processing failed")
            )

        return {
            "project_id": project_id,
            "status": "completed",
            "input_file": file.filename,
            "output_file": result["filename"],
            "output_path": result["output_path"],
            "silence_segments_removed": result["silence_segments_removed"],
            "timeline_segments": result["timeline_segments"],
            "message": "Video processing completed successfully ✂️"
        }

    except HTTPException:
        raise
    except Exception as e:
        if video_path.exists():
            video_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))
