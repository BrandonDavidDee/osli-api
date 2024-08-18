import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError

from app.authentication.models import AccessTokenData
from app.authentication.scopes import process_required_scopes, process_user_scopes

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


async def get_source_id(source_id: int | None = None) -> int | None:
    # FastApi will grab this if it's in the path or if it's in a query parameter
    return source_id


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(get_token_from_header)],
    source_id: int | None = Depends(get_source_id),
) -> AccessTokenData:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
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

    # skip all subsequent scope processing
    if "is_admin" in token_data.scopes:
        return token_data

    user_scopes = process_user_scopes(token_scopes, source_id)
    required_scopes = process_required_scopes(security_scopes.scopes, source_id)

    for scope in required_scopes:
        if scope not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
            )

    return token_data
