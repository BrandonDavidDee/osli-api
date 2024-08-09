from fastapi import APIRouter, Depends, Response

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.models import ItemLink, ItemTag, SearchParams
from app.items.vimeo.controllers.item_create import ItemVimeoCreateController
from app.items.vimeo.controllers.item_detail import ItemVimeoDetailController
from app.items.vimeo.controllers.item_links import ItemVimeoLinkController
from app.items.vimeo.controllers.item_list import ItemVimeoListController
from app.items.vimeo.controllers.item_save import ItemVimeoSaveController
from app.items.vimeo.controllers.item_tags import ItemVimeoTagsController
from app.items.vimeo.models import ItemVimeo

router = APIRouter()


@router.post("")
async def item_batch_upload(
    source_id: int,
    encryption_key: str,
    payload: ItemVimeo,
    token_data: AccessTokenData = Depends(get_current_user),
):
    controller = ItemVimeoCreateController(token_data, source_id)
    return await controller.item_create(encryption_key, payload)


@router.post("/search")
async def item_vimeo_list(
    source_id: int,
    payload: SearchParams,
    token_data: AccessTokenData = Depends(get_current_user),
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


@router.post("/{item_id}/links")
async def item_link_create(
    item_id: int,
    payload: ItemLink,
    token_data: AccessTokenData = Depends(get_current_user),
):
    controller = ItemVimeoLinkController(token_data, item_id)
    return await controller.item_link_create(payload)


@router.get("/{item_id}/links")
async def item_links(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    controller = ItemVimeoLinkController(token_data, item_id)
    return await controller.get_item_links()


@router.put("/{item_id}/links/{item_link_id}")
async def item_link_update(
    item_id: int,
    item_link_id: int,
    payload: ItemLink,
    token_data: AccessTokenData = Depends(get_current_user),
):
    controller = ItemVimeoLinkController(token_data, item_id)
    return await controller.item_link_update(item_link_id, payload)


@router.delete("/{item_id}/links/{item_link_id}")
async def item_link_delete(
    item_id: int,
    item_link_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
):
    controller = ItemVimeoLinkController(token_data, item_id)
    return await controller.item_link_delete(item_link_id)


@router.post("/{item_id}/save")
async def save_item(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    return await ItemVimeoSaveController(token_data, item_id).save_item()


@router.delete("/{item_id}/save")
async def delete_saved_item(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    return await ItemVimeoSaveController(token_data, item_id).delete_saved_item()
