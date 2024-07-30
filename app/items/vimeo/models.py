from pydantic import BaseModel

from app.sources.s3.models import SourceS3
from app.items.models import ItemBase
from app.tags.models import Tag


class ItemTag(BaseModel):
    id: int
    tag: Tag


class ItemVimeo(ItemBase):
    mime_type: str | None = None
    file_path: str
    file_name: str | None = None
    file_size: int | None = None
    source: SourceS3 | None = None
