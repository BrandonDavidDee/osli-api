from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.items.bucket.models import ItemBucket
from app.items.vimeo.models import ItemVimeo


class GalleryItem(BaseModel):
    id: int
    item_order: int = 0
    item_bucket: Optional[ItemBucket] = None
    item_vimeo: Optional[ItemVimeo] = None


class Gallery(BaseModel):
    id: int | None = None
    title: str
    description: str | None = None
    date_created: datetime | None = None
    # created_by_id: int | None = None
    items: list[GalleryItem] = []
