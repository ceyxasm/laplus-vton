from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.routers import products, tryon

# Create FastAPI app
app = FastAPI(
    title="LaPlus VTON API",
    description="Virtual Try-On API for LaPlus Fashion",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Include routers
app.include_router(products.router)
app.include_router(tryon.router)


@app.get("/")
async def root():
    return {
        "message": "LaPlus VTON API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    import os
    raw = os.environ.get("GEMINI_API_KEY", "")
    return {
        "status": "healthy",
        "mock_mode": settings.mock_mode,
        "gemini_configured": bool(settings.gemini_api_key),
        "raw_key_set": bool(raw),
        "settings_key_set": bool(settings.gemini_api_key)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
