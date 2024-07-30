from pydantic import BaseModel


class SourceBase(BaseModel):
    id: int
    name: str
    grid_view: bool = False
