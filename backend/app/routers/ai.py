from fastapi import APIRouter

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

@router.post("/generate")
async def generate():
    return {"message": "AI generation endpoint"}

@router.post("/process")
async def process():
    return {"message": "AI processing endpoint"}
