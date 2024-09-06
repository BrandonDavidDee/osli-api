from fastapi import APIRouter, Depends, Response, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.models import ItemLink, ItemTag, SearchParams
from app.items.vimeo.controllers.item_create import ItemVimeoCreateController
from app.items.vimeo.controllers.item_delete import ItemVimeoDeleteController
from app.items.vimeo.controllers.item_detail import ItemVimeoDetailController
from app.items.vimeo.controllers.item_links import ItemVimeoLinkController
from app.items.vimeo.controllers.item_list import ItemVimeoListController
from app.items.vimeo.controllers.item_save import ItemVimeoSaveController
from app.items.vimeo.controllers.item_tags import ItemVimeoTagsController
from app.items.vimeo.models import ItemVimeo

router = APIRouter()


@router.post("")
async def item_vimeo_create(
    source_id: int,
    encryption_key: str,
    payload: ItemVimeo,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["vimeo_{source_id}_item_create"]
    ),
) -> int:
    controller = ItemVimeoCreateController(token_data, source_id)
    return await controller.item_create(encryption_key, payload)


@router.post("/search")
async def item_vimeo_list(
    source_id: int,
    payload: SearchParams,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["vimeo_{source_id}_item_read"]
    ),
) -> dict:
    controller = ItemVimeoListController(token_data, source_id)
    return await controller.item_search(payload)


@router.get("/{item_id}")
async def item_detail(
    source_id: int,
    item_id: int,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["vimeo_{source_id}_item_read"]
    ),
) -> ItemVimeo:
    return await ItemVimeoDetailController(token_data, source_id, item_id).item_detail()


@router.put("/{item_id}")
async def item_update(
    source_id: int,
    item_id: int,
    payload: ItemVimeo,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["vimeo_{source_id}_item_update"]
    ),
) -> ItemVimeo:
    return await ItemVimeoDetailController(token_data, source_id, item_id).item_update(
        payload
    )


@router.delete("/{item_id}")
async def item_delete(
    source_id: int,
    item_id: int,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["vimeo_{source_id}_item_delete"]
    ),
) -> int:
    controller = ItemVimeoDeleteController(token_data, source_id)
    return await controller.delete_item(item_id)


@router.put("/{item_id}/vimeo-meta")
async def item_update_vimeo_meta(
    encryption_key: str,
    source_id: int,
    item_id: int,
    payload: ItemVimeo,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["vimeo_{source_id}_item_update"]
    ),
) -> ItemVimeo:
    return await ItemVimeoDetailController(
        token_data, source_id, item_id
    ).item_update_vimeo_meta(encryption_key, payload)


@router.get("/{item_id}/related")
async def get_related(
    source_id: int,
    item_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
) -> dict:
    return await ItemVimeoDetailController(token_data, source_id, item_id).get_related()


@router.post("/{item_id}/tags")
async def item_tag_create(
    source_id: int,
    item_id: int,
    payload: ItemTag,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["vimeo_{source_id}_item_update"]
    ),
) -> ItemTag:
    controller = ItemVimeoTagsController(token_data, item_id)
    return await controller.item_tag_create(payload)


@router.delete("/{item_id}/tags/{tag_item_vimeo_id}")
async def item_tag_delete(
    source_id: int,
    item_id: int,
    tag_item_vimeo_id: int,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["vimeo_{source_id}_item_update"]
    ),
) -> Response:
    controller = ItemVimeoTagsController(token_data, item_id)
    return await controller.item_tag_delete(tag_item_vimeo_id)


@router.post("/{item_id}/links")
async def item_link_create(
    item_id: int,
    payload: ItemLink,
    token_data: AccessTokenData = Depends(get_current_user),
) -> ItemLink:
    controller = ItemVimeoLinkController(token_data, item_id)
    return await controller.item_link_create(payload)


@router.get("/{item_id}/links")
async def item_links(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
) -> ItemVimeo:
    controller = ItemVimeoLinkController(token_data, item_id)
    return await controller.get_item_links()


@router.put("/{item_id}/links/{item_link_id}")
async def item_link_update(
    item_id: int,
    item_link_id: int,
    payload: ItemLink,
    token_data: AccessTokenData = Depends(get_current_user),
) -> ItemLink:
    controller = ItemVimeoLinkController(token_data, item_id)
    return await controller.item_link_update(item_link_id, payload)


@router.delete("/{item_id}/links/{item_link_id}")
async def item_link_delete(
    item_id: int,
    item_link_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
) -> int:
    controller = ItemVimeoLinkController(token_data, item_id)
    return await controller.item_link_delete(item_link_id)


@router.post("/{item_id}/save")
async def save_item(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
) -> None:
    return await ItemVimeoSaveController(token_data, item_id).save_item()


@router.delete("/{item_id}/save")
async def delete_saved_item(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
) -> None:
    return await ItemVimeoSaveController(token_data, item_id).delete_saved_item()
