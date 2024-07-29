from pydantic import BaseModel


class LoginBody(BaseModel):
    username: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenData(BaseModel):
    username: str


class AccessTokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
