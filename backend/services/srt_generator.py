import os
import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Segment:
    """Subtitle segment."""
    
    def __init__(self, index: int, start: float, end: float, text: str):
        self.index = index
        self.start = start
        self.end = end
        self.text = text
    
    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,MMM)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def to_srt_format(self) -> str:
        """Format segment as SRT subtitle."""
        return (
            f"{self.index}\n"
            f"{self.format_timestamp(self.start)} --> {self.format_timestamp(self.end)}\n"
            f"{self.text}\n"
        )


class SRTGenerator:
    """Service for generating SRT subtitle files."""
    
    @staticmethod
    def generate_from_segments(
        whisper_segments: List[dict],
        output_path: str,
        max_chars_per_line: int = 42
    ) -> bool:
        """
        Generate SRT file from Whisper transcription segments.
        
        Args:
            whisper_segments: List of segments from Whisper transcription
            output_path: Path to output SRT file
            max_chars_per_line: Maximum characters per subtitle line
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            segments = []
            for idx, seg in enumerate(whisper_segments, 1):
                text = seg.get("text", "").strip()
                if text:
                    # Wrap text if needed
                    wrapped_text = SRTGenerator._wrap_text(text, max_chars_per_line)
                    segment = Segment(
                        index=idx,
                        start=seg.get("start", 0),
                        end=seg.get("end", 0),
                        text=wrapped_text
                    )
                    segments.append(segment)
            
            # Write SRT file
            with open(output_path, "w", encoding="utf-8") as f:
                for segment in segments:
                    f.write(segment.to_srt_format())
                    f.write("\n")
            
            logger.info(f"SRT file generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating SRT file: {str(e)}")
            return False
    
    @staticmethod
    def _wrap_text(text: str, max_chars: int) -> str:
        """Wrap text to specified character width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if sum(len(w) for w in current_line) + len(current_line) + len(word) > max_chars:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return "\n".join(lines)
    
    @staticmethod
    def read_srt(srt_path: str) -> Optional[List[dict]]:
        """
        Read and parse SRT file.
        
        Returns:
            List of segments with index, start, end, and text
        """
        try:
            segments = []
            with open(srt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            # Split by double newlines
            subtitle_blocks = content.split("\n\n")
            
            for block in subtitle_blocks:
                lines = block.strip().split("\n")
                if len(lines) >= 3:
                    try:
                        index = int(lines[0])
                        timestamps = lines[1].split(" --> ")
                        start = SRTGenerator._parse_timestamp(timestamps[0].strip())
                        end = SRTGenerator._parse_timestamp(timestamps[1].strip())
                        text = "\n".join(lines[2:])
                        
                        segments.append({
                            "index": index,
                            "start": start,
                            "end": end,
                            "text": text
                        })
                    except (ValueError, IndexError):
                        continue
            
            return segments
            
        except Exception as e:
            logger.error(f"Error reading SRT file: {str(e)}")
            return None
    
    @staticmethod
    def _parse_timestamp(timestamp_str: str) -> float:
        """Parse SRT timestamp to seconds."""
        # Format: HH:MM:SS,MMM
        parts = timestamp_str.replace(",", ".").split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
