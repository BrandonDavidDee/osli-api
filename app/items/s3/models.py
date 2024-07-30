from datetime import datetime

from pydantic import BaseModel

from app.sources.s3.models import Source
from app.tags.models import Tag


class SearchParams(BaseModel):
    source: Source | None = None
    limit: int = 10
    offset: int = 0
    filter: str = ""
    tag_ids: list[int] = []


class ItemTag(BaseModel):
    id: int
    tag: Tag


class Item(BaseModel):
    id: int | None = None
    mime_type: str | None = None
    file_path: str
    file_name: str | None = None
    file_size: int | None = None
    notes: str | None = None
    date_created: datetime
    created_by: str
    source: Source | None = None
    tags: list[ItemTag] = []
