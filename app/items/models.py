from datetime import date, datetime

from pydantic import BaseModel

from app.tags.models import Tag
from app.users.models import User


class SearchParams(BaseModel):
    limit: int = 10
    offset: int = 0
    filter: str = ""
    tag_ids: list[int] = []


class ItemTag(BaseModel):
    id: int | None = None
    tag: Tag


class ItemLink(BaseModel):
    id: int | None = None
    title: str | None = None
    link: str
    expiration_date: datetime | None = None
    view_count: int = 0
    date_created: date | None = None
    created_by: User | None = None


class ItemBase(BaseModel):
    id: int | None = None
    notes: str | None = None
    date_created: datetime
    created_by_id: int
    tags: list[ItemTag] = []
    links: list[ItemLink] = []
    created_by: User | None = None
