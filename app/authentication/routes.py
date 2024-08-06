from typing import Annotated

from fastapi import APIRouter, Depends, Request, Security

from app.authentication.controller import LoginController, RefreshController
from app.authentication.models import AccessTokenData, LoginBody
from app.authentication.token import get_current_user

router = APIRouter()


@router.post("/login")
async def login(body: LoginBody, request: Request):
    return await LoginController(request).login(body)


@router.post("/refresh-tokens")
async def refresh_tokens(request: Request):
    return await RefreshController(request).refresh_tokens()


@router.get("/me")
async def read_users_me(
    token_data: Annotated[AccessTokenData, Depends(get_current_user)],
):
    return token_data


@router.get("/me/items")
async def read_own_items(
    token_data: Annotated[
        AccessTokenData, Security(get_current_user, scopes=["items"])
    ],
):
    return [{"item_id": "Foo", "owner": token_data.user_id}]
