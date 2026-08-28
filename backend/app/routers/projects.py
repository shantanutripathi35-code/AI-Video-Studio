from fastapi import APIRouter

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

@router.get("/")
async def list_projects():
    return {"message": "List projects endpoint"}

@router.post("/")
async def create_project():
    return {"message": "Create project endpoint"}
