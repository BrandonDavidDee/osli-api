from fastapi import APIRouter, Depends

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.galleries.controllers.gallery_detail import GalleryDetailController
from app.galleries.controllers.gallery_links import GalleryLinkController
from app.galleries.controllers.gallery_list import GalleryListController
from app.galleries.models import GalleryLink

router = APIRouter()


@router.get("")
async def gallery_list(token_data: AccessTokenData = Depends(get_current_user)):
    controller = GalleryListController(token_data)
    return await controller.get_galleries()


@router.get("/{gallery_id}")
async def gallery_detail(
    gallery_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    controller = GalleryDetailController(token_data, gallery_id)
    return await controller.get_gallery_detail()


@router.post("/{gallery_id}/links")
async def gallery_link_create(
    gallery_id: int,
    payload: GalleryLink,
    token_data: AccessTokenData = Depends(get_current_user),
):
    controller = GalleryLinkController(token_data, gallery_id)
    return await controller.gallery_link_create(payload)


@router.get("/{gallery_id}/links")
async def gallery_links(
    gallery_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    controller = GalleryLinkController(token_data, gallery_id)
    return await controller.get_gallery_links()


@router.put("/{gallery_id}/links/{gallery_link_id}")
async def gallery_link_update(
    gallery_id: int,
    gallery_link_id: int,
    payload: GalleryLink,
    token_data: AccessTokenData = Depends(get_current_user),
):
    controller = GalleryLinkController(token_data, gallery_id)
    return await controller.gallery_link_update(gallery_link_id, payload)


@router.delete("/{gallery_id}/links/{gallery_link_id}")
async def gallery_link_delete(
    gallery_id: int,
    gallery_link_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
):
    controller = GalleryLinkController(token_data, gallery_id)
    return await controller.gallery_link_delete(gallery_link_id)
