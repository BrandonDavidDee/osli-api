from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.items.bucket.models import ItemBucket
from app.items.vimeo.models import ItemVimeo
from app.sources.models import SourceType


class SavedItem(BaseModel):
    source_type: SourceType
    item_bucket: Optional[ItemBucket] = None
    item_vimeo: Optional[ItemVimeo] = None
    date_saved: datetime
