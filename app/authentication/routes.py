from fastapi import APIRouter, Depends, Request

from app.authentication.controller import LoginController, RefreshController
from app.authentication.models import AccessTokenData, LoginBody, TokenPair
from app.authentication.permissions import (
    PermissionGroup,
    dynamic_bucket_permissions,
    dynamic_vimeo_permissions,
    miscellaneous_permissions,
    permission_groups,
)
from app.authentication.token import get_current_user

router = APIRouter()


@router.post("/login")
async def login(body: LoginBody, request: Request) -> TokenPair:
    return await LoginController(request).login(body)


@router.post("/refresh-tokens")
async def refresh_tokens(request: Request) -> TokenPair:
    return await RefreshController(request).refresh_tokens()


@router.get("/permissions")
def get_permissions(
    token_data: AccessTokenData = Depends(get_current_user),
) -> dict:
    return {
        "bucket": dynamic_bucket_permissions,
        "vimeo": dynamic_vimeo_permissions,
        "miscellaneous": miscellaneous_permissions,
    }


@router.get("/permission-groups")
def get_permission_groups(
    token_data: AccessTokenData = Depends(get_current_user),
) -> list[PermissionGroup]:
    return permission_groups
