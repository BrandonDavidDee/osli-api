from datetime import datetime

from pydantic import BaseModel

from app.tags.models import Tag


class SearchParams(BaseModel):
    limit: int = 10
    offset: int = 0
    filter: str = ""
    tag_ids: list[int] = []


class ItemTag(BaseModel):
    id: int | None = None
    tag: Tag


class ItemBase(BaseModel):
    id: int | None = None
    notes: str | None = None
    date_created: datetime
    created_by_id: int
    tags: list[ItemTag] = []
