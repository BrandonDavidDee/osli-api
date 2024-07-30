from enum import Enum
from pydantic import BaseModel


class SourceType(str, Enum):
    S3 = "s3"
    VIMEO = "vimeo"


class SourceBase(BaseModel):
    id: int
    name: str
    grid_view: bool = False
    source_type: SourceType
