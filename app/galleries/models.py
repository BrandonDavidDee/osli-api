from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.items.bucket.models import ItemBucket
from app.sources.models import SourceType
from app.items.vimeo.models import ItemVimeo
from app.users.models import User


class GalleryItem(BaseModel):
    id: int
    item_order: int = 0
    source_type: SourceType | None = None
    item_bucket: Optional[ItemBucket] = None
    item_vimeo: Optional[ItemVimeo] = None


class GalleryLinks(BaseModel):
    id: int
    title: str | None = None
    link: str
    expiration_date: datetime | None = None
    view_count: int = 0
    date_created: datetime
    # created_by_id: int | None = None


class Gallery(BaseModel):
    id: int | None = None
    title: str
    description: str | None = None
    date_created: datetime | None = None
    created_by: User | None = None
    items: list[GalleryItem] = []
    links: list[GalleryLinks] = []
