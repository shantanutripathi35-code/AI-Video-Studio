from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
from uuid import uuid4
import whisper
from datetime import timedelta

router = APIRouter(prefix="/ai", tags=["AI Processing"])

UPLOAD_DIR = Path("storage/uploads")
OUTPUT_DIR = Path("storage/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
MAX_SIZE = 500 * 1024 * 1024  # 500 MB

# Initialize Whisper model
whisper_model = whisper.load_model("base")


def format_time(seconds):
    td = timedelta(seconds=seconds)
    total = td.total_seconds()

    h = int(total // 3600)
    m = int((total % 3600) // 60)
    s = int(total % 60)
    ms = int((total - int(total)) * 1000)

    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def save_srt(result, output):
    with open(output, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], start=1):
            f.write(f"{i}\n")
            f.write(
                f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n"
            )
            f.write(seg["text"].strip() + "\n\n")


def extract_audio(video_path: str):
    """Extract audio from video file using FFmpeg"""
    import subprocess
    
    audio_path = str(OUTPUT_DIR / f"{uuid4()}.mp3")
    
    try:
        subprocess.run([
            "ffmpeg",
            "-i", video_path,
            "-q:a", "9",
            "-n",
            audio_path
        ], check=True, capture_output=True)
        return audio_path
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to extract audio")


@router.post("/caption")
async def process_caption(file: UploadFile = File(...)):
    """
    Complete video processing pipeline:
    Upload → Extract Audio → Transcribe → Generate SRT
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
    video_path = UPLOAD_DIR / f"{project_id}{extension}"

    # Upload video with chunking
    size = 0
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

    try:
        # Extract audio from video
        audio_path = extract_audio(str(video_path))

        # Transcribe audio with Whisper
        result = whisper_model.transcribe(
            audio_path,
            task="transcribe"
        )

        # Extract transcribed text
        full_text = " ".join([seg["text"] for seg in result["segments"]])

        # Generate SRT subtitle file
        srt_path = OUTPUT_DIR / f"{project_id}.srt"
        save_srt(result, str(srt_path))

        return {
            "project_id": project_id,
            "language": result.get("language", "en"),
            "text": full_text,
            "subtitle": f"{project_id}.srt",
            "status": "completed",
            "segments": result["segments"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
