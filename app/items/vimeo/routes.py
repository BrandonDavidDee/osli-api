from typing import Annotated

from fastapi import APIRouter, Depends, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.models import SearchParams
from app.items.vimeo.controller import (
    ItemVimeoDetailController,
    ItemVimeoListController,
)
from app.items.vimeo.models import ItemVimeo

router = APIRouter()


@router.post("")
async def item_vimeo_list(
    source_id: int,
    payload: SearchParams,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    controller = ItemVimeoListController(token_data, source_id)
    return await controller.item_search(payload)


@router.get("/{item_id}")
async def item_detail(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    return await ItemVimeoDetailController(token_data, item_id).item_detail()


@router.put("/{item_id}")
async def item_update(
    item_id: int,
    payload: ItemVimeo,
    token_data: AccessTokenData = Depends(get_current_user),
):
    return await ItemVimeoDetailController(token_data, item_id).item_update(payload)
