from pydantic import BaseModel


class LoginBody(BaseModel):
    username: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenData(BaseModel):
    user_id: str


class AccessTokenData(BaseModel):
    user_id: str | None = None
    scopes: list[str] = []
