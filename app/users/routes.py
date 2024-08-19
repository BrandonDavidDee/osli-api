from fastapi import APIRouter, Depends, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.users.controllers.user_detail import UserDetailController
from app.users.controllers.user_list import UserListController
from app.users.models import User, UserDetail

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
    token_data: AccessTokenData = Security(get_current_user, scopes=["is_admin"]),
) -> UserDetail:
    controller = UserDetailController(token_data, user_id)
    return await controller.get_user_detail()
