from sqlalchemy import Column, String, Integer, DateTime, Boolean, LargeBinary, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.database import Base


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    EXTRACTING_AUDIO = "extracting_audio"
    TRANSCRIBING = "transcribing"
    GENERATING_CAPTIONS = "generating_captions"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoProject(Base):
    __tablename__ = "video_projects"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    project_name = Column(String, nullable=False)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    
    # Configuration
    target_duration = Column(Integer, default=30)
    aspect_ratio = Column(String, default="9:16")
    enable_captions = Column(Boolean, default=True)
    remove_silence = Column(Boolean, default=False)
    voice_enhancement = Column(Boolean, default=False)
    
    # File paths
    original_video_path = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)
    transcript_path = Column(String, nullable=True)
    srt_path = Column(String, nullable=True)
    output_video_path = Column(String, nullable=True)
    
    # Metadata
    original_duration = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)
    progress_percentage = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<VideoProject(id={self.id}, status={self.status})>"
