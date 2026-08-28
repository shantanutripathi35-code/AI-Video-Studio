from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VideoProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None


class VideoProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class VideoProjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    video_path: Optional[str]
    audio_path: Optional[str]
    transcript: Optional[str]
    srt_content: Optional[str]
    output_video_path: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    size: int
    path: str
    status: str
