from app.sources.models import SourceBase


class SourceBucket(SourceBase):
    bucket_name: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None
    media_prefix: str | None = None
