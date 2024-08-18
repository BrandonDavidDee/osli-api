from fastapi import APIRouter, Request

from app.authentication.controller import LoginController, RefreshController
from app.authentication.models import LoginBody, TokenPair
from app.authentication.scopes import dynamic_permissions, permission_groups

router = APIRouter()


@router.post("/login")
async def login(body: LoginBody, request: Request) -> TokenPair:
    return await LoginController(request).login(body)


@router.post("/refresh-tokens")
async def refresh_tokens(request: Request) -> TokenPair:
    return await RefreshController(request).refresh_tokens()


@router.get("/scopes")
def get_scopes():
    return dynamic_permissions


@router.get("/scope-groups")
def get_scope_groups():
    return permission_groups
