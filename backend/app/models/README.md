# Models

SQLAlchemy ORM models for database tables.

## VideoProject Model

Represents a video project with metadata and processing status.

### Fields
- `id`: Unique identifier (UUID)
- `user_id`: Owner of the project
- `title`: Project title
- `description`: Project description
- `video_path`: Path to uploaded video file
- `audio_path`: Path to extracted audio
- `transcript`: Generated transcript from Whisper
- `srt_content`: SRT subtitle content
- `output_video_path`: Path to final video with subtitles
- `status`: Processing status (uploaded, processing, completed, failed)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `error_message`: Error details if processing failed

## User Model

Represents application users.

### Fields
- `id`: Unique identifier
- `email`: User email address
- `hashed_password`: Hashed password
- `is_active`: Account active status
- `created_at`: Account creation timestamp
