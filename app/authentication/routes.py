from fastapi import APIRouter, Request

from app.authentication.controller import LoginController, RefreshController
from app.authentication.models import LoginBody, TokenPair

# from app.authentication.scopes import all_scopes, all_groups

router = APIRouter()


@router.post("/login")
async def login(body: LoginBody, request: Request) -> TokenPair:
    return await LoginController(request).login(body)


@router.post("/refresh-tokens")
async def refresh_tokens(request: Request) -> TokenPair:
    return await RefreshController(request).refresh_tokens()


# @router.get("/scopes")
# def get_scopes():
#     return all_scopes
#
#
# @router.get("/scope-groups")
# def get_scope_groups():
#     return all_groups
