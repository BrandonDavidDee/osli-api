from fastapi import APIRouter, Depends, Response

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.galleries.controllers.gallery_detail import GalleryDetailController
from app.galleries.controllers.gallery_links import (
    GalleryLinkController,
    GalleryLinkUpdateController,
)
from app.galleries.controllers.gallery_list import GalleryListController
from app.galleries.models import Gallery, GalleryItem, GalleryLink

router = APIRouter()


@router.post("")
async def gallery_create(
    payload: Gallery, token_data: AccessTokenData = Depends(get_current_user)
) -> int:
    controller = GalleryListController(token_data)
    return await controller.gallery_create(payload)


@router.get("")
async def gallery_list(
    token_data: AccessTokenData = Depends(get_current_user),
) -> list[Gallery]:
    controller = GalleryListController(token_data)
    return await controller.get_galleries()


@router.get("/{gallery_id}")
async def gallery_detail(
    gallery_id: int, token_data: AccessTokenData = Depends(get_current_user)
) -> Gallery:
    controller = GalleryDetailController(token_data, gallery_id)
    return await controller.get_gallery_detail()


@router.put("/{gallery_id}")
async def gallery_update(
    gallery_id: int,
    payload: Gallery,
    token_data: AccessTokenData = Depends(get_current_user),
) -> Gallery:
    controller = GalleryDetailController(token_data, gallery_id)
    return await controller.gallery_update(payload)


@router.post("/{gallery_id}/items")
async def gallery_item_create(
    gallery_id: int,
    payload: GalleryItem,
    token_data: AccessTokenData = Depends(get_current_user),
) -> GalleryItem:
    controller = GalleryDetailController(token_data, gallery_id)
    return await controller.gallery_item_create(payload)


@router.delete("/{gallery_id}/items/{gallery_item_id}")
async def gallery_item_delete(
    gallery_id: int,
    gallery_item_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
) -> int:
    controller = GalleryDetailController(token_data, gallery_id)
    return await controller.gallery_item_delete(gallery_item_id)


@router.post("/{gallery_id}/links")
async def gallery_link_create(
    gallery_id: int,
    payload: GalleryLink,
    token_data: AccessTokenData = Depends(get_current_user),
) -> GalleryLink:
    controller = GalleryLinkController(token_data, gallery_id)
    return await controller.gallery_link_create(payload)


@router.get("/{gallery_id}/links")
async def gallery_links(
    gallery_id: int, token_data: AccessTokenData = Depends(get_current_user)
) -> Gallery:
    controller = GalleryLinkController(token_data, gallery_id)
    return await controller.get_gallery_links()


@router.put("/{gallery_id}/links/{gallery_link_id}")
async def gallery_link_update(
    gallery_id: int,
    gallery_link_id: int,
    payload: GalleryLink,
    link_only: bool = False,
    token_data: AccessTokenData = Depends(get_current_user),
) -> GalleryLink:
    if link_only:
        controller = GalleryLinkUpdateController(token_data)
        return await controller.link_only_update(gallery_link_id, payload)
    controller = GalleryLinkController(token_data, gallery_id)
    return await controller.gallery_link_update(gallery_link_id, payload)


@router.delete("/{gallery_id}/links/{gallery_link_id}")
async def gallery_link_delete(
    gallery_id: int,
    gallery_link_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
) -> int:
    controller = GalleryLinkController(token_data, gallery_id)
    return await controller.gallery_link_delete(gallery_link_id)


@router.get("/link-availability/{link}")
async def link_availability_check(
    link: str, token_data: AccessTokenData = Depends(get_current_user)
) -> bool:
    controller = GalleryLinkUpdateController(token_data)
    return await controller.link_availability(link)
