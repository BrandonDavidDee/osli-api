import os
from typing import Annotated, Callable

from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from pydantic import ValidationError

from app.authentication.models import AccessTokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 5 * 24 * 60  # 5 days


def get_token_from_header(authorization: str = Header(None)) -> str:
    try:
        token = authorization.partition(" ")[2]
    except (AttributeError, IndexError):
        raise HTTPException(status_code=401)
    return token


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_header)],
    security_scope: str | None = None,
) -> AccessTokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = AccessTokenData(scopes=token_scopes, user_id=user_id)
    except (JWTError, ValidationError):
        raise credentials_exception

    if security_scope is None:
        return token_data

    if "is_admin" in token_data.scopes:
        return token_data

    if security_scope not in token_scopes:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
        )

    return token_data


async def get_source_id(source_id: int | None = None) -> int | None:
    return source_id


def get_authorized_user(permission_level: str | None = None) -> Callable:
    async def _get_token(
        source_id: int | None = Depends(get_source_id),
        token: str = Depends(get_token_from_header),
    ) -> AccessTokenData:
        security_scope = None
        if source_id and permission_level:
            security_scope = f"{permission_level}:{source_id}"
        elif permission_level:
            security_scope = permission_level
        return await get_current_user(token, security_scope)

    return _get_token
