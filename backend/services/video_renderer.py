import subprocess
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)


class VideoRenderer:
    """Service for rendering video with captions and applying effects."""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
    
    def render_with_subtitles(
        self,
        input_video: str,
        srt_path: str,
        output_path: str,
        aspect_ratio: str = "9:16",
        target_duration: Optional[int] = None
    ) -> bool:
        """
        Render video with embedded subtitles.
        
        Args:
            input_video: Path to input video
            srt_path: Path to SRT subtitle file
            output_path: Path to output video
            aspect_ratio: Target aspect ratio (e.g., "9:16")
            target_duration: Target duration in seconds (optional)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Build FFmpeg filter for subtitles and aspect ratio
            filter_complex = self._build_filter_complex(srt_path, aspect_ratio)
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_video,
                "-vf", filter_complex,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-y",  # Overwrite output
                output_path
            ]
            
            # Add duration limit if specified
            if target_duration:
                cmd.insert(2, "-t")
                cmd.insert(3, str(target_duration))
            
            logger.info(f"Rendering video with subtitles: {output_path}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=7200  # 2 hours
            )
            
            if result.returncode == 0:
                logger.info("Video rendered successfully")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Video rendering timed out")
            return False
        except Exception as e:
            logger.error(f"Error rendering video: {str(e)}")
            return False
    
    def _build_filter_complex(self, srt_path: str, aspect_ratio: str) -> str:
        """Build FFmpeg filter complex for subtitles and aspect ratio."""
        filters = []
        
        # Add subtitle filter
        srt_file = srt_path.replace("\\", "\\\\").replace(":", "\\:")
        filters.append(f"subtitles='{srt_file}'")
        
        # Add aspect ratio scaling
        if aspect_ratio == "9:16":
            # Vertical format - adjust height while maintaining aspect
            filters.append("scale='min(iw,ih*9/16)':ih")
        elif aspect_ratio == "16:9":
            # Horizontal format
            filters.append("scale=iw:'min(ih,iw*9/16)'")
        
        return ",".join(filters)
    
    def remove_silence(
        self,
        input_video: str,
        output_path: str,
        silence_threshold: float = -40.0,
        min_silence_duration: float = 0.5
    ) -> bool:
        """
        Remove silence from video.
        
        Args:
            input_video: Path to input video
            output_path: Path to output video
            silence_threshold: Audio level threshold in dB
            min_silence_duration: Minimum duration of silence to remove
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # FFmpeg filter to remove silence
            afilter = (
                f"silenceremove="
                f"start_periods=1:"
                f"start_duration=1:"
                f"start_threshold={silence_threshold}dB:"
                f"stop_periods=-1:"
                f"stop_duration={min_silence_duration}:"
                f"stop_threshold={silence_threshold}dB"
            )
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_video,
                "-af", afilter,
                "-c:v", "copy",
                "-y",
                output_path
            ]
            
            logger.info(f"Removing silence from video: {output_path}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode == 0:
                logger.info("Silence removed successfully")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing silence: {str(e)}")
            return False
