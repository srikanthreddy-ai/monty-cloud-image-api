import os, shutil
from uuid import uuid4
from datetime import datetime
from fastapi.responses import FileResponse
from fastapi import HTTPException
from app.models.schemas import ImageMetadata

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

IMAGES_DB = []  # Replace with database later


async def save_image(file, description, tags):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")

    image_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{image_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    metadata = ImageMetadata(
        id=image_id,
        filename=file.filename,
        description=description,
        tags=[t.strip() for t in tags.split(",") if t.strip()],
        upload_time=datetime.utcnow()
    )

    IMAGES_DB.append({**metadata.dict(), "path": file_path})
    return metadata


def list_images(tag=None, filename=None):
    results = IMAGES_DB
    if tag:
        results = [img for img in results if tag in img["tags"]]
    if filename:
        results = [img for img in results if filename.lower() in img["filename"].lower()]
    return [ImageMetadata(**img) for img in results]


def get_image_file(image_id):
    for img in IMAGES_DB:
        if img["id"] == image_id:
            return FileResponse(img["path"], filename=img["filename"])
    raise HTTPException(status_code=404, detail="Image not found")


def delete_image(image_id):
    global IMAGES_DB
    for img in IMAGES_DB:
        if img["id"] == image_id:
            try:
                os.remove(img["path"])
            except FileNotFoundError:
                pass
            IMAGES_DB = [i for i in IMAGES_DB if i["id"] != image_id]
            return {"message": "Image deleted successfully"}
    raise HTTPException(status_code=404, detail="Image not found")
