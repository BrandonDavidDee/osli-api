import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError

from app.authentication.models import AccessTokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 5 * 24 * 60  # 5 days


SCOPE_HIERARCHY = {
    "admin": ["admin", "edit", "view"],  # can view, edit, delete
    "edit": ["edit", "view"],  # view, create, and edit items but cannot delete them
    "view": ["view"],  # view items but cannot edit or delete them
}


def get_token_from_header(authorization: str = Header(None)) -> str:
    try:
        token = authorization.partition(" ")[2]
    except (AttributeError, IndexError):
        raise HTTPException(status_code=401)
    return token


def parse_dynamic_scope(scope: str, source_id: int | None = None) -> str:
    if not source_id:
        return scope
    scope_map = {
        "admin": f"{source_id}:admin",
        "view": f"{source_id}:view",
        "edit": f"{source_id}:edit",
    }
    return scope_map.get(scope, scope)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(get_token_from_header)],
    source_id: int | None = None,
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

    # Expand the user's scopes based on the above SCOPE_HIERARCHY
    if source_id:
        expanded_scopes = set()
        for user_scope in token_data.scopes:
            base_scope = user_scope.split(":")[1] if ":" in user_scope else user_scope
            expanded_scopes.update(SCOPE_HIERARCHY.get(base_scope, []))

        expanded_scopes = {f"{source_id}:{scope}" for scope in expanded_scopes}
    else:
        expanded_scopes = token_data.scopes

    for scope in security_scopes.scopes:
        parsed_scope = parse_dynamic_scope(scope, source_id)
        if parsed_scope not in expanded_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
            )
    return token_data
