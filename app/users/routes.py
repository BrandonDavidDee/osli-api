from fastapi import APIRouter, Depends, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.users.controllers.user_detail import UserDetailController
from app.users.controllers.user_list import UserListController
from app.users.models import User

router = APIRouter()


@router.get("")
async def user_list(
    token_data: AccessTokenData = Depends(get_current_user),
) -> list[User]:
    controller = UserListController(token_data)
    return await controller.get_list()


@router.get("/{user_id}")
async def user_detail(
    user_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
) -> User:
    controller = UserDetailController(token_data, user_id)
    return await controller.get_user_detail()


@router.put("/{user_id}/scopes")
async def update_user_scopes(
    user_id: int,
    payload: User,
    token_data: AccessTokenData = Security(get_current_user, scopes=["is_admin"]),
) -> User:
    controller = UserDetailController(token_data, user_id)
    return await controller.update_user_scopes(payload)
