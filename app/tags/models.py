from pydantic import BaseModel


class Tag(BaseModel):
    id: int | None = None
    title: str
