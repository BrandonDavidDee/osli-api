from datetime import datetime

from pydantic import BaseModel

from app.sources.models import SourceConfig
from app.tags.models import Tag


class SearchParams(BaseModel):
    source_config: SourceConfig | None = None
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
    source_config: SourceConfig | None = None
    tags: list[ItemTag] = []
