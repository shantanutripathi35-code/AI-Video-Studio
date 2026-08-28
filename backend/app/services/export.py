import subprocess
from pathlib import Path
from uuid import uuid4
from enum import Enum
from datetime import datetime
from typing import Optional, List, Tuple

class ExportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ExportJob:
    def __init__(self, job_id: str, input_path: str, timeline: List[Tuple[float, float]]):
        self.job_id = job_id
        self.input_path = input_path
        self.timeline = timeline
        self.status = ExportStatus.PENDING
        self.progress = 0
        self.output_path: Optional[str] = None
        self.error: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

class ExportService:
    def __init__(self, output_dir: str = "storage/exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.jobs: dict[str, ExportJob] = {}

    def create_export_job(self, input_path: str, timeline: List[Tuple[float, float]]) -> ExportJob:
        """Create a new export job"""
        job_id = str(uuid4())
        job = ExportJob(job_id, input_path, timeline)
        self.jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[ExportJob]:
        """Get export job by ID"""
        return self.jobs.get(job_id)

    def build_ffmpeg_filter(self, timeline: List[Tuple[float, float]]) -> str:
        """Build FFmpeg filter_complex for timeline segments"""
        if not timeline:
            raise ValueError("Timeline cannot be empty")

        filter_parts = []
        
        # Create trim and concat filters for video and audio
        for i, (start, end) in enumerate(timeline):
            filter_parts.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]")
            filter_parts.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]")

        # Build concat filter
        concat_v = "".join([f"[v{i}]" for i in range(len(timeline))])
        concat_a = "".join([f"[a{i}]" for i in range(len(timeline))])
        concat_filter = f"{concat_v}concat=n={len(timeline)}:v=1:a=1[outv];{concat_a}concat=n={len(timeline)}:v=0:a=1[outa]"

        return ";".join(filter_parts + [concat_filter])

    def render_export(self, job: ExportJob) -> bool:
        """Render video with timeline applied"""
        try:
            job.status = ExportStatus.PROCESSING
            job.started_at = datetime.utcnow()
            job.progress = 10

            # Build output path
            output_filename = f"export_{job.job_id}.mp4"
            output_path = self.output_dir / output_filename

            # Build FFmpeg filter
            filter_complex = self.build_ffmpeg_filter(job.timeline)

            # Build FFmpeg command for MP4 export
            cmd = [
                "ffmpeg",
                "-i", job.input_path,
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-map", "[outa]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-progress", "pipe:1",
                "-y",
                str(output_path)
            ]

            # Execute FFmpeg with progress tracking
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Parse progress
            for line in process.stdout:
                if line.startswith("out_time_ms="):
                    # Update progress (simplified for demo)
                    job.progress = min(95, job.progress + 5)
                elif line.startswith("progress=end"):
                    job.progress = 100

            process.wait()

            if process.returncode != 0:
                error_output = process.stderr.read() if process.stderr else "Unknown error"
                raise Exception(f"FFmpeg failed: {error_output}")

            job.output_path = str(output_path)
            job.progress = 100
            job.status = ExportStatus.COMPLETED
            job.completed_at = datetime.utcnow()

            return True

        except Exception as e:
            job.status = ExportStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            return False

    def get_download_url(self, job_id: str) -> Optional[str]:
        """Generate download URL for completed export"""
        job = self.get_job(job_id)
        if not job or job.status != ExportStatus.COMPLETED:
            return None
        
        return f"/api/export/download/{job_id}"

    def get_job_status(self, job_id: str) -> dict:
        """Get detailed job status"""
        job = self.get_job(job_id)
        if not job:
            return {"error": "Job not found"}

        status_data = {
            "job_id": job.job_id,
            "status": job.status.value,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        }

        if job.status == ExportStatus.COMPLETED:
            status_data["download_url"] = self.get_download_url(job_id)
            status_data["output_file"] = Path(job.output_path).name if job.output_path else None
        
        if job.status == ExportStatus.FAILED:
            status_data["error"] = job.error

        return status_data
