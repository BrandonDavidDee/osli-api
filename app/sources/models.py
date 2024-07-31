from enum import Enum

from pydantic import BaseModel


class SourceType(str, Enum):
    BUCKET = "bucket"
    VIMEO = "vimeo"


class SourceBase(BaseModel):
    id: int
    name: str
    grid_view: bool = False
    source_type: SourceType
