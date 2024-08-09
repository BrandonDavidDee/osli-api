from fastapi import APIRouter, Depends, Request

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
async def read_users_me(token_data: AccessTokenData = Depends(get_current_user)):
    return token_data


@router.get("/me/items")
async def read_own_items(token_data: AccessTokenData = Depends(get_current_user)):
    return [{"item_id": "Foo", "owner": token_data.user_id}]
