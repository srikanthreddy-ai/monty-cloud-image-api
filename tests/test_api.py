import sys, os, io
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.services.image_service import IMAGES_DB 
client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_after_tests():
    """Cleanup uploads directory and reset IMAGES_DB after each test."""
    yield
    for img in list(IMAGES_DB):
        try:
            os.remove(img["path"])
        except FileNotFoundError:
            pass
    IMAGES_DB.clear()


def test_upload_image():
    """Test uploading a valid image"""
    file_data = io.BytesIO(os.urandom(10))  # dummy binary content
    response = client.post(
        "/images/upload",
        files={"file": ("sample.jpg", file_data, "image/jpeg")},
        data={"description": "test image", "tags": "test,photo"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["filename"] == "sample.jpg"
    assert data["description"] == "test image"
    assert "upload_time" in data
    assert isinstance(data["tags"], list)
    assert "test" in data["tags"]


def test_upload_invalid_file_type():
    """Test uploading a non-image file"""
    file_data = io.BytesIO(b"Not an image")
    response = client.post(
        "/images/upload",
        files={"file": ("text.txt", file_data, "text/plain")},
        data={"description": "bad file"},
    )

    assert response.status_code == 400


def test_list_images():
    """Test listing all images"""
    file_data = io.BytesIO(os.urandom(10))
    client.post(
        "/images/upload",
        files={"file": ("sample.jpg", file_data, "image/jpeg")},
        data={"description": "desc", "tags": "alpha,beta"},
    )

    response = client.get("/images")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["filename"] == "sample.jpg"


def test_filter_images_by_tag():
    """Test filtering by tag"""
    for tag in ["cat", "dog"]:
        file_data = io.BytesIO(os.urandom(10))
        client.post(
            "/images/upload",
            files={"file": (f"{tag}.jpg", file_data, "image/jpeg")},
            data={"tags": tag},
        )

    response = client.get("/images", params={"tag": "dog"})
    assert response.status_code == 200
    data = response.json()
    assert all("dog" in img["tags"] for img in data)
    assert len(data) == 1


def test_download_image():
    """Test downloading an existing image"""
    file_data = io.BytesIO(os.urandom(10))
    upload_response = client.post(
        "/images/upload",
        files={"file": ("sample.jpg", file_data, "image/jpeg")},
        data={"tags": "download"},
    )
    image_id = upload_response.json()["id"]

    response = client.get(f"/images/{image_id}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")


def test_download_nonexistent_image():
    """Test downloading non-existing image"""
    response = client.get("/images/12345")
    assert response.status_code == 404
    assert "Image not found" in response.text


def test_delete_image():
    """Test deleting an existing image"""
    file_data = io.BytesIO(os.urandom(10))
    upload_response = client.post(
        "/images/upload",
        files={"file": ("sample.jpg", file_data, "image/jpeg")},
        data={"tags": "delete"},
    )
    image_id = upload_response.json()["id"]

    delete_response = client.delete(f"/images/{image_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Image deleted successfully"
    response = client.get(f"/images/{image_id}")
    assert response.status_code == 404


def test_delete_nonexistent_image():
    """Test deleting non-existing image"""
    response = client.delete("/images/nonexistent-id")
    assert response.status_code == 404
    assert "Image not found" in response.text
