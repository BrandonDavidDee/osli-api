from app.sources.models import SourceBase


class SourceS3(SourceBase):
    bucket_name: str
    access_key_id: str | None = None
    secret_access_key: str | None = None
    media_prefix: str | None = None
