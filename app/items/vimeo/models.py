from pydantic import BaseModel

from app.items.models import ItemBase
from app.sources.vimeo.models import SourceVimeo
from app.tags.models import Tag


class ItemTag(BaseModel):
    id: int
    tag: Tag


class ItemVimeo(ItemBase):
    title: str | None = None
    thumbnail: str | None = None
    video_id: str
    source: SourceVimeo | None = None
