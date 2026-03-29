from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import uuid
import time
import os
import shutil
from typing import Optional, Dict
import asyncio

from app.models.product import TryOnJob
from app.services.gemini_service import gemini_service
from app.config import settings

router = APIRouter(prefix="/api/tryon", tags=["tryon"])

# In-memory job storage (for POC)
jobs: Dict[str, TryOnJob] = {}


@router.post("/start")
async def start_tryon(
    product_id: str = Form(...),
    person_image: UploadFile = File(...),
    custom_prompt: Optional[str] = Form(None)
):
    """
    Start a virtual try-on job

    Args:
        product_id: ID of the product to try on
        person_image: User's photo (from camera)
        custom_prompt: Optional styling prompt

    Returns:
        job_id: ID to poll for results
    """

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save uploaded image
    person_image_path = os.path.join(settings.upload_dir, f"{job_id}_person.jpg")

    try:
        with open(person_image_path, "wb") as buffer:
            shutil.copyfileobj(person_image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    # Create job
    job = TryOnJob(
        job_id=job_id,
        product_id=product_id,
        status="pending",
        created_at=time.time()
    )

    jobs[job_id] = job

    # Start async processing
    asyncio.create_task(process_tryon(job_id, person_image_path, product_id, custom_prompt))

    return {"job_id": job_id, "status": "pending"}


async def process_tryon(
    job_id: str,
    person_image_path: str,
    product_id: str,
    custom_prompt: Optional[str]
):
    """Background task to process try-on"""

    job = jobs.get(job_id)
    if not job:
        return

    # Update status
    job.status = "processing"

    try:
        # Get garment image path
        # Convert product ID to image filename (e.g., "shirt-001" -> "shirt-1.jpg")
        product_parts = product_id.rsplit('-', 1)
        if len(product_parts) == 2:
            category = product_parts[0]
            number = product_parts[1].lstrip('0') or '1'
            garment_filename = f"{category}-{number}.jpg"
        else:
            garment_filename = f"{product_id}.jpg"

        # Use absolute path to product images bundled with backend
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        garment_image_path = os.path.join(backend_dir, "data", "images", garment_filename)

        # Generate try-on with Gemini
        result = await gemini_service.generate_tryon(
            person_image_path=person_image_path,
            garment_image_path=garment_image_path,
            custom_prompt=custom_prompt
        )

        if result["status"] == "success":
            # Gemini service already saved the image
            result_image_path = result.get("image_path")

            if result_image_path and os.path.exists(result_image_path):
                # Get just the filename for the URL
                result_filename = os.path.basename(result_image_path)
                base = settings.backend_url.rstrip("/") if settings.backend_url else ""
                job.result_image_url = f"{base}/uploads/{result_filename}"
                job.status = "completed"
                job.completed_at = time.time()
            else:
                job.status = "failed"
                job.error_message = "Generated image not found"
                job.completed_at = time.time()
        else:
            job.status = "failed"
            job.error_message = result.get("message", "Unknown error")
            job.completed_at = time.time()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = time.time()


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Poll for job status"""

    job = jobs.get(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.post("/regenerate/{job_id}")
async def regenerate_tryon(
    job_id: str,
    custom_prompt: str = Form(...)
):
    """Regenerate try-on with new prompt"""

    old_job = jobs.get(job_id)

    if not old_job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Create new job with same images
    new_job_id = str(uuid.uuid4())
    person_image_path = os.path.join(settings.upload_dir, f"{job_id}_person.jpg")

    # Check if original image exists
    if not os.path.exists(person_image_path):
        raise HTTPException(status_code=404, detail="Original image not found")

    # Create new job
    new_job = TryOnJob(
        job_id=new_job_id,
        product_id=old_job.product_id,
        status="pending",
        created_at=time.time()
    )

    jobs[new_job_id] = new_job

    # Start processing with new prompt
    asyncio.create_task(process_tryon(
        new_job_id,
        person_image_path,
        old_job.product_id,
        custom_prompt
    ))

    return {"job_id": new_job_id, "status": "pending"}
