from pydantic import BaseModel


class User(BaseModel):
    id: int | None = None
    is_active: bool
    is_admin: bool = False
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    scopes: list[str] = []


class UserInDB(User):
    hashed_password: str
