from datetime import datetime

from pydantic import BaseModel

from app.authentication.permissions import Permission


class User(BaseModel):
    id: int | None = None
    is_active: bool
    is_admin: bool = False
    username: str
    notes: str | None = None
    scopes: list[str] = []  # the raw scope values stored in db
    date_created: datetime | None = None


class UserInDB(User):
    hashed_password: str


class UserDetail(User):
    permissions: list[
        Permission
    ] = []  # individual permissions extrapolated from scopes
