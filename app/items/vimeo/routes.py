from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.models import ItemTag, SearchParams
from app.items.vimeo.controllers.item_detail import ItemVimeoDetailController
from app.items.vimeo.controllers.item_list import ItemVimeoListController
from app.items.vimeo.controllers.item_tags import ItemVimeoTagsController
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


@router.post("/{item_id}/tags")
async def item_tag_create(
    item_id: int,
    payload: ItemTag,
    token_data: AccessTokenData = Depends(get_current_user),
) -> ItemTag:
    controller = ItemVimeoTagsController(token_data, item_id)
    return await controller.item_tag_create(payload)


@router.delete("/{item_id}/tags/{tag_item_vimeo_id}")
async def item_tag_delete(
    item_id: int,
    tag_item_vimeo_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
) -> Response:
    controller = ItemVimeoTagsController(token_data, item_id)
    return await controller.item_tag_delete(tag_item_vimeo_id)
