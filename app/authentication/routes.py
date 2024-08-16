from fastapi import APIRouter, Request

from app.authentication.controller import LoginController, RefreshController
from app.authentication.models import LoginBody, TokenPair

router = APIRouter()


@router.post("/login")
async def login(body: LoginBody, request: Request) -> TokenPair:
    return await LoginController(request).login(body)


@router.post("/refresh-tokens")
async def refresh_tokens(request: Request) -> TokenPair:
    return await RefreshController(request).refresh_tokens()
