from app.items.models import ItemBase
from app.sources.bucket.models import SourceBucket


class ItemBucket(ItemBase):
    title: str | None = None
    mime_type: str | None = None
    file_path: str  # this is the key & full path including directory
    file_name: str | None = None  # this is just the file name for display
    file_size: int | None = None
    source: SourceBucket | None = None
