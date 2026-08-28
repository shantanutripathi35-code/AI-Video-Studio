# Services

Business logic and service layer.

## AudioExtractorService

Extracts audio tracks from video files using FFmpeg.

### Methods
- `extract_audio(video_path: str) -> str`: Extract audio and return path
- `validate_audio(audio_path: str) -> bool`: Validate extracted audio file

## WhisperService

Generates transcriptions from audio using OpenAI Whisper.

### Methods
- `transcribe(audio_path: str) -> dict`: Transcribe audio to text
- `get_model_size()`: Get current model size (tiny, base, small, medium, large)

## SRTGeneratorService

Generates SRT subtitle files from transcriptions.

### Methods
- `generate_srt(transcript: dict) -> str`: Create SRT content from transcript
- `save_srt(content: str, path: str) -> bool`: Save SRT file to disk

## VideoRendererService

Renders videos with embedded subtitles.

### Methods
- `render_with_subtitles(video_path: str, srt_path: str) -> str`: Render video with subtitles
- `change_aspect_ratio(video_path: str, ratio: str) -> str`: Convert video aspect ratio

## VideoPipelineService

Orchestrates the complete video processing workflow.

### Methods
- `process_video(project_id: str, video_path: str) -> bool`: Run complete pipeline
- `get_status(project_id: str) -> dict`: Get processing status
