import whisper
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class WhisperService:
    """Service for speech-to-text using OpenAI Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper service.
        
        Args:
            model_name: Model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
    
    def load_model(self) -> bool:
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            return False
    
    def transcribe(self, audio_path: str) -> Optional[Dict]:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with transcription result or None if error
        """
        try:
            if self.model is None:
                if not self.load_model():
                    return None
            
            logger.info(f"Transcribing audio: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                language="en",
                verbose=False
            )
            
            logger.info(f"Transcription completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
    
    def get_segments(self, audio_path: str) -> Optional[list]:
        """
        Get transcription segments with timestamps.
        
        Returns:
            List of segments with start, end, and text
        """
        result = self.transcribe(audio_path)
        if result is None:
            return None
        
        return result.get("segments", [])
