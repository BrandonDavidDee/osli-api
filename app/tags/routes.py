from fastapi import APIRouter, Depends

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.tags.controller import TagController
from app.tags.models import Tag

router = APIRouter()


@router.get("", response_model=list[Tag])
async def get_tags(
    token_data: AccessTokenData = Depends(get_current_user),
) -> list[Tag]:
    controller = TagController(token_data)
    return await controller.get_list()
