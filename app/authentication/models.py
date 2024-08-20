from pydantic import BaseModel

from app.users.models import User


class LoginBody(BaseModel):
    username: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    user: User


class RefreshTokenData(BaseModel):
    user_id: str


class AccessTokenData(BaseModel):
    user_id: str | None = None
    scopes: list[str] = []
