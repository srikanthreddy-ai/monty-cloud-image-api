from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ImageMetadata(BaseModel):
    id: str
    filename: str
    description: Optional[str]
    tags: Optional[List[str]] = []
    upload_time: datetime
