import logging
import os
import uuid
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.video_project import VideoProject, ProcessingStatus
from backend.services.audio_extractor import AudioExtractor
from backend.services.whisper_service import WhisperService
from backend.services.srt_generator import SRTGenerator
from backend.services.video_renderer import VideoRenderer
from backend.core.config import settings

logger = logging.getLogger(__name__)


class VideoPipeline:
    """Main orchestrator for video processing pipeline."""
    
    def __init__(self):
        self.audio_extractor = AudioExtractor(settings.FFMPEG_PATH)
        self.whisper_service = WhisperService(settings.WHISPER_MODEL)
        self.srt_generator = SRTGenerator()
        self.video_renderer = VideoRenderer(settings.FFMPEG_PATH)
    
    def create_project(
        self,
        db: Session,
        user_id: str,
        project_name: str,
        target_duration: int,
        aspect_ratio: str,
        enable_captions: bool,
        remove_silence: bool,
        voice_enhancement: bool
    ) -> VideoProject:
        """Create a new video project."""
        project_id = str(uuid.uuid4())
        
        project = VideoProject(
            id=project_id,
            user_id=user_id,
            project_name=project_name,
            status=ProcessingStatus.PENDING,
            target_duration=target_duration,
            aspect_ratio=aspect_ratio,
            enable_captions=enable_captions,
            remove_silence=remove_silence,
            voice_enhancement=voice_enhancement,
            progress_percentage=0
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        logger.info(f"Created project: {project_id}")
        return project
    
    def process_video(
        self,
        db: Session,
        project: VideoProject,
        video_path: str
    ) -> bool:
        """
        Execute the complete video processing pipeline.
        
        Pipeline steps:
        1. Upload → Extract Audio
        2. Extract Audio → Whisper Speech-to-Text
        3. Whisper → Generate SRT
        4. Generate SRT → Render MP4
        5. Return Subtitle
        """
        try:
            # Step 1: Store original video path
            project.original_video_path = video_path
            project.status = ProcessingStatus.UPLOADING
            project.progress_percentage = 10
            db.commit()
            logger.info(f"[{project.id}] Step 1: Video uploaded")
            
            # Step 2: Extract Audio
            project.status = ProcessingStatus.EXTRACTING_AUDIO
            project.progress_percentage = 20
            db.commit()
            
            audio_path = self._get_project_file_path(project, "audio.mp3")
            if not self.audio_extractor.extract_audio(video_path, audio_path):
                raise Exception("Audio extraction failed")
            
            project.audio_path = audio_path
            project.progress_percentage = 30
            db.commit()
            logger.info(f"[{project.id}] Step 2: Audio extracted")
            
            # Step 3: Transcribe with Whisper
            project.status = ProcessingStatus.TRANSCRIBING
            project.progress_percentage = 40
            db.commit()
            
            whisper_result = self.whisper_service.transcribe(audio_path)
            if not whisper_result:
                raise Exception("Whisper transcription failed")
            
            segments = whisper_result.get("segments", [])
            project.progress_percentage = 50
            db.commit()
            logger.info(f"[{project.id}] Step 3: Audio transcribed ({len(segments)} segments)")
            
            # Step 4: Generate SRT Captions
            project.status = ProcessingStatus.GENERATING_CAPTIONS
            project.progress_percentage = 60
            db.commit()
            
            srt_path = self._get_project_file_path(project, "captions.srt")
            if not self.srt_generator.generate_from_segments(segments, srt_path):
                raise Exception("SRT generation failed")
            
            project.srt_path = srt_path
            project.progress_percentage = 70
            db.commit()
            logger.info(f"[{project.id}] Step 4: Captions generated")
            
            # Step 5: Apply effects and render
            project.status = ProcessingStatus.RENDERING
            project.progress_percentage = 80
            db.commit()
            
            output_path = self._get_project_file_path(project, "output.mp4")
            
            # Handle silence removal if enabled
            render_input = video_path
            if project.remove_silence:
                temp_output = self._get_project_file_path(project, "temp_no_silence.mp4")
                if self.video_renderer.remove_silence(video_path, temp_output):
                    render_input = temp_output
                    logger.info(f"[{project.id}] Silence removed")
            
            # Apply voice enhancement if enabled (placeholder)
            if project.voice_enhancement:
                logger.info(f"[{project.id}] Voice enhancement enabled (placeholder)")
            
            # Render with subtitles and aspect ratio
            if not self.video_renderer.render_with_subtitles(
                render_input,
                srt_path,
                output_path,
                project.aspect_ratio,
                project.target_duration
            ):
                raise Exception("Video rendering failed")
            
            project.output_video_path = output_path
            project.status = ProcessingStatus.COMPLETED
            project.progress_percentage = 100
            db.commit()
            logger.info(f"[{project.id}] Step 5: Video rendered and completed")
            
            return True
            
        except Exception as e:
            logger.error(f"[{project.id}] Pipeline error: {str(e)}")
            project.status = ProcessingStatus.FAILED
            project.error_message = str(e)
            db.commit()
            return False
    
    def _get_project_file_path(self, project: VideoProject, filename: str) -> str:
        """Get storage path for project files."""
        project_dir = os.path.join(
            settings.UPLOAD_DIR,
            project.user_id,
            project.id
        )
        os.makedirs(project_dir, exist_ok=True)
        return os.path.join(project_dir, filename)
    
    def get_project_status(self, db: Session, project_id: str) -> Optional[VideoProject]:
        """Get current status of a project."""
        return db.query(VideoProject).filter(VideoProject.id == project_id).first()
