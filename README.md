# AI Video Studio

Video editing application with AI-powered subtitle generation.

## Features

- **Video Upload & Processing**: Upload videos and automatically process them
- **Audio Extraction**: Extract audio from video files using FFmpeg
- **Speech-to-Text**: Generate transcriptions using OpenAI Whisper
- **SRT Subtitle Generation**: Automatically create SRT subtitle files
- **Video Rendering**: Render videos with embedded subtitles
- **Silence Removal**: Optional silence detection and removal
- **Voice Enhancement**: Optional voice enhancement features
- **Aspect Ratio Support**: Support for various aspect ratios (9:16, 16:9, etc.)
- **Flutter Mobile App**: Native mobile app for iOS and Android

## Architecture

### Backend (Python/FastAPI)
```
Upload Video
      ↓
Extract Audio (FFmpeg)
      ↓
Whisper Speech-to-Text
      ↓
Generate SRT
      ↓
Return Subtitle
      ↓
Flutter Preview
```

### Project Structure
```
backend/
├── core/
│   └── config.py           # Configuration management
├── models/
│   └── video_project.py    # Database models
├── schemas/
│   └── video_schemas.py    # Pydantic schemas
├── services/
│   ├── audio_extractor.py  # Audio extraction service
│   ├── whisper_service.py  # Speech-to-text service
│   ├── srt_generator.py    # Subtitle generation
│   ├── video_renderer.py   # Video rendering with effects
│   └── video_pipeline.py   # Pipeline orchestration
├── routes/
│   └── videos.py           # API endpoints
├── database.py             # Database configuration
└── main.py                 # FastAPI application

mobile/
└── (Flutter app)
```

## API Endpoints

### Video Projects
- `POST /api/videos/projects` - Create new video project
- `GET /api/videos/projects/{project_id}` - Get project status
- `POST /api/videos/projects/{project_id}/upload` - Upload video file
- `GET /api/videos/projects/{project_id}/subtitle` - Get SRT subtitles
- `GET /api/videos/projects/{project_id}/download` - Download processed video

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL
- FFmpeg
- CUDA (optional, for GPU acceleration)

### Setup

1. Clone the repository
```bash
git clone https://github.com/shantanutripathi35-code/AI-Video-Studio.git
cd AI-Video-Studio
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

5. Initialize database
```bash
python -m backend.database
```

6. Run the server
```bash
python -m backend.main
```

The API will be available at `http://localhost:8000`

## Configuration

Edit `backend/.env`:
```
DATABASE_URL=postgresql+psycopg://user:password@localhost/aivideo
SECRET_KEY=your-secret-key
WHISPER_MODEL=base  # tiny, base, small, medium, large
UPLOAD_DIR=storage/uploads
MAX_UPLOAD_SIZE=500000000  # 500MB
```

## Processing Pipeline

1. **Upload** - User uploads video file
2. **Extract Audio** - FFmpeg extracts audio track
3. **Whisper** - OpenAI Whisper generates transcript with timestamps
4. **Generate Captions** - Create SRT subtitle file
5. **Detect Silence** (optional) - Identify and optionally remove silent sections
6. **Cut Video** (optional) - Remove silence segments
7. **Render MP4** - Re-encode video with embedded subtitles
8. **Preview** - Display result in Flutter app

## Technologies

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Video Processing**: FFmpeg
- **Speech-to-Text**: OpenAI Whisper
- **Mobile**: Flutter (Dart)
- **Database**: PostgreSQL
- **Authentication**: JWT (Python-Jose)

## Development

### Running Tests
```bash
pytest
```

### Code Style
```bash
black backend/
flake8 backend/
```

## License

MIT License

## Support

For issues and feature requests, please open an issue on GitHub.
