from fastapi import APIRouter, Depends

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.tags.controller import TagController
from app.tags.models import Tag

router = APIRouter()


@router.post("")
async def tag_create():
    pass


@router.get("")
async def tag_list(
    token_data: AccessTokenData = Depends(get_current_user),
) -> list[Tag]:
    controller = TagController(token_data)
    return await controller.get_list()


@router.put("/{tag_id}")
async def tag_update(tag_id: int):
    pass


@router.delete("/{tag_id}")
async def tag_delete(tag_id: int):
    pass


@router.get("/{tag_id}/related")
async def tag_related():
    pass
