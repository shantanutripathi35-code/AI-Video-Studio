from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ProcessingStatusEnum(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    EXTRACTING_AUDIO = "extracting_audio"
    TRANSCRIBING = "transcribing"
    GENERATING_CAPTIONS = "generating_captions"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoConfigCreate(BaseModel):
    target_duration: int = 30
    aspect_ratio: str = "9:16"
    enable_captions: bool = True
    remove_silence: bool = False
    voice_enhancement: bool = False


class VideoProjectCreate(BaseModel):
    project_name: str
    config: VideoConfigCreate


class VideoProjectResponse(BaseModel):
    id: str
    user_id: str
    project_name: str
    status: ProcessingStatusEnum
    target_duration: int
    aspect_ratio: str
    enable_captions: bool
    remove_silence: bool
    voice_enhancement: bool
    original_video_path: Optional[str]
    srt_path: Optional[str]
    output_video_path: Optional[str]
    progress_percentage: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubtitleResponse(BaseModel):
    project_id: str
    srt_content: str
    status: ProcessingStatusEnum
    progress_percentage: int
    error_message: Optional[str]
