import subprocess
import re
from pathlib import Path
from uuid import uuid4
from datetime import timedelta

class SmartCutService:
    def __init__(self, output_dir: str = "storage/outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def detect_silence(self, video_path: str):
        """
        Detect silent segments in video using FFmpeg
        Returns list of tuples: (silence_start, silence_end)
        """
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-af", "silencedetect=noise=-30dB:d=0.5",
            "-f", "null",
            "-"
        ]

        result = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            text=True
        )

        pattern = r"silence_start: ([0-9.]+)|silence_end: ([0-9.]+)"
        matches = re.findall(pattern, result.stderr)
        
        # Parse silence segments
        silence_segments = []
        for i in range(0, len(matches), 2):
            if i + 1 < len(matches):
                start = float(matches[i][0]) if matches[i][0] else 0
                end = float(matches[i + 1][1]) if matches[i + 1][1] else 0
                if start and end:
                    silence_segments.append((start, end))
        
        return silence_segments

    def build_edit_timeline(self, video_path: str, silence_segments: list, min_segment_duration: float = 0.5):
        """
        Build edit timeline by removing silence segments
        Returns list of (start, end) tuples for segments to keep
        """
        # Get video duration
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1:noval=1",
            video_path
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        duration = float(result.stdout.strip())

        # Build timeline by keeping non-silent segments
        timeline = []
        current_start = 0

        for silence_start, silence_end in sorted(silence_segments):
            if silence_start > current_start:
                segment_duration = silence_start - current_start
                if segment_duration >= min_segment_duration:
                    timeline.append((current_start, silence_start))
            current_start = silence_end

        # Add final segment if it's not silent
        if current_start < duration:
            timeline.append((current_start, duration))

        return timeline

    def render_video(self, video_path: str, timeline: list, output_path: str):
        """
        Render new video with only non-silent segments
        Creates a filter_complex command to concat segments
        """
        if not timeline:
            raise ValueError("No valid segments in timeline")

        # Build ffmpeg filter for concatenating segments
        filter_parts = []
        for i, (start, end) in enumerate(timeline):
            filter_parts.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]")
            filter_parts.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]")

        # Concatenate all segments
        concat_v = "".join([f"[v{i}]" for i in range(len(timeline))])
        concat_a = "".join([f"[a{i}]" for i in range(len(timeline))])
        concat_filter = f"{concat_v}concat=n={len(timeline)}:v=1:a=1[outv];{concat_a}concat=n={len(timeline)}:v=0:a=1[outa]"

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-filter_complex", ";".join(filter_parts + [concat_filter]),
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            output_path
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def process_smart_cut(self, video_path: str):
        """
        Complete Smart Cut pipeline:
        1. Detect silence
        2. Build edit timeline
        3. Render video
        4. Return output path
        """
        try:
            # Detect silence segments
            silence_segments = self.detect_silence(video_path)

            # Build edit timeline (segments to keep)
            timeline = self.build_edit_timeline(video_path, silence_segments)

            if not timeline:
                raise ValueError("No valid segments found after removing silence")

            # Generate output path
            output_filename = f"smartcut_{uuid4()}.mp4"
            output_path = self.output_dir / output_filename

            # Render video
            self.render_video(video_path, timeline, str(output_path))

            return {
                "success": True,
                "output_path": str(output_path),
                "filename": output_filename,
                "silence_segments_removed": len(silence_segments),
                "timeline_segments": len(timeline)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
