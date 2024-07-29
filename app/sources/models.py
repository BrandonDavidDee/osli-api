from pydantic import BaseModel


class SourceConfig(BaseModel):
    id: int
    name: str
    bucket_name: str
    access_key_id: str | None = None
    secret_access_key: str | None = None
    media_prefix: str | None = None
    grid_view: bool = False
