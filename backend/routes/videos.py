from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.schemas.video_schemas import (
    VideoProjectCreate,
    VideoProjectResponse,
    SubtitleResponse,
    ProcessingStatusEnum
)
from backend.services.video_pipeline import VideoPipeline
from backend.models.video_project import VideoProject
from backend.core.config import settings
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/videos", tags=["videos"])

pipeline = VideoPipeline()


@router.post("/projects", response_model=VideoProjectResponse)
async def create_video_project(
    project_data: VideoProjectCreate,
    db: Session = Depends(get_db),
    user_id: str = "user_001"  # In production, extract from JWT token
) -> VideoProjectResponse:
    """Create a new video processing project."""
    try:
        project = pipeline.create_project(
            db=db,
            user_id=user_id,
            project_name=project_data.project_name,
            target_duration=project_data.config.target_duration,
            aspect_ratio=project_data.config.aspect_ratio,
            enable_captions=project_data.config.enable_captions,
            remove_silence=project_data.config.remove_silence,
            voice_enhancement=project_data.config.voice_enhancement
        )
        return VideoProjectResponse.from_orm(project)
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create project")


@router.post("/projects/{project_id}/upload")
async def upload_video(
    project_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Upload video file and start processing pipeline."""
    try:
        # Get project
        project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate file size
        file_size = await file.seek(0, 2)
        await file.seek(0)
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large (max {settings.MAX_UPLOAD_SIZE} bytes)"
            )
        
        # Save uploaded file
        upload_dir = os.path.join(settings.UPLOAD_DIR, project.user_id, project_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        video_path = os.path.join(upload_dir, "original.mp4")
        with open(video_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        logger.info(f"Video uploaded for project {project_id}: {video_path}")
        
        # Start processing in background
        if background_tasks:
            background_tasks.add_task(
                pipeline.process_video,
                db,
                project,
                video_path
            )
        
        return {
            "project_id": project_id,
            "status": "processing_started",
            "message": "Video uploaded and processing started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload video")


@router.get("/projects/{project_id}", response_model=VideoProjectResponse)
async def get_project_status(
    project_id: str,
    db: Session = Depends(get_db)
) -> VideoProjectResponse:
    """Get current status of a video project."""
    try:
        project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return VideoProjectResponse.from_orm(project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get project status")


@router.get("/projects/{project_id}/subtitle", response_model=SubtitleResponse)
async def get_subtitle(
    project_id: str,
    db: Session = Depends(get_db)
) -> SubtitleResponse:
    """Get subtitle (SRT) file for a completed project."""
    try:
        project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if captions are available
        if not project.srt_path or not os.path.exists(project.srt_path):
            raise HTTPException(status_code=404, detail="Subtitles not found")
        
        # Read SRT content
        with open(project.srt_path, "r", encoding="utf-8") as f:
            srt_content = f.read()
        
        return SubtitleResponse(
            project_id=project_id,
            srt_content=srt_content,
            status=project.status,
            progress_percentage=project.progress_percentage,
            error_message=project.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subtitle: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get subtitle")


@router.get("/projects/{project_id}/download")
async def download_video(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Download processed video file."""
    try:
        project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if not project.output_video_path or not os.path.exists(project.output_video_path):
            raise HTTPException(status_code=404, detail="Video not found or still processing")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            project.output_video_path,
            filename=f"{project.project_name}.mp4",
            media_type="video/mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download video")
