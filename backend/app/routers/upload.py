from fastapi import APIRouter

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

@router.post("/video")
async def upload_video():
    return {"message": "Upload video endpoint"}

@router.post("/image")
async def upload_image():
    return {"message": "Upload image endpoint"}
