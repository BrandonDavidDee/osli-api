from fastapi import APIRouter, Depends

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.item_links.controller import ItemLinkController
from app.items.models import ItemLink

router = APIRouter()


@router.put("/{item_link_id}")
async def item_link_update(
    item_link_id: int,
    payload: ItemLink,
    token_data: AccessTokenData = Depends(get_current_user),
):
    controller = ItemLinkController(token_data)
    return await controller.link_update(item_link_id, payload)


@router.get("/availability/{link}")
async def link_availability_check(
    link: str, token_data: AccessTokenData = Depends(get_current_user)
):
    controller = ItemLinkController(token_data)
    return await controller.link_availability(link)
