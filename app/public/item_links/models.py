from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.items.bucket.models import ItemBucket
from app.items.vimeo.models import ItemVimeo
from app.sources.models import SourceType


class PublicItemLink(BaseModel):
    title: str | None = None
    expiration_date: date | None = None
    source_type: SourceType | None = None
    item_bucket: Optional[ItemBucket] | None = None
    item_vimeo: Optional[ItemVimeo] | None = None
