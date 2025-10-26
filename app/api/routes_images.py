from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.image_service import save_image, list_images, get_image_file, delete_image

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), description: str = Form(""), tags: str = Form("")):
    return await save_image(file, description, tags)

@router.get("/")
def get_images(tag: str = None, filename: str = None):
    return list_images(tag, filename)

@router.get("/{image_id}")
def view_image(image_id: str):
    return get_image_file(image_id)

@router.delete("/{image_id}")
def remove_image(image_id: str):
    return delete_image(image_id)
