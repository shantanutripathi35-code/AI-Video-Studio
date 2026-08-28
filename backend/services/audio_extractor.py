import subprocess
import os
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AudioExtractor:
    """Service for extracting audio from video using FFmpeg."""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
    
    def extract_audio(
        self,
        video_path: str,
        output_audio_path: str,
        audio_format: str = "mp3"
    ) -> bool:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to input video file
            output_audio_path: Path to output audio file
            audio_format: Audio format (mp3, wav, aac, etc.)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
            
            # FFmpeg command to extract audio
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-q:a", "0",
                "-map", "a",
                "-y",  # Overwrite output file
                output_audio_path
            ]
            
            logger.info(f"Extracting audio from {video_path}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Audio extracted successfully to {output_audio_path}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Audio extraction timed out")
            return False
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            return False
    
    def get_audio_duration(self, audio_path: str) -> Optional[float]:
        """Get duration of audio file in seconds."""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", audio_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse duration from stderr
            for line in result.stderr.split('\n'):
                if 'Duration:' in line:
                    # Example: Duration: 00:02:30.50
                    duration_str = line.split('Duration:')[1].split(',')[0].strip()
                    parts = duration_str.split(':')
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = float(parts[2])
                    return hours * 3600 + minutes * 60 + seconds
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            return None
