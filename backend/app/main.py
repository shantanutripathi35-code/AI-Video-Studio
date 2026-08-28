from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="AI Video Studio API",
    description="Backend API for AI Video Studio",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "AI Video Studio API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
