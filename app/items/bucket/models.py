from pydantic import BaseModel

from app.items.models import ItemBase
from app.sources.bucket.models import SourceBucket
from app.tags.models import Tag


class ItemTag(BaseModel):
    id: int
    tag: Tag


class ItemBucket(ItemBase):
    title: str | None = None
    mime_type: str | None = None
    file_path: str
    file_name: str | None = None
    file_size: int | None = None
    source: SourceBucket | None = None
