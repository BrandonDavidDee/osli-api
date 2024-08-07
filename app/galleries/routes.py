from fastapi import APIRouter, Depends

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.galleries.controllers.gallery_detail import GalleryDetailController
from app.galleries.controllers.gallery_list import GalleryListController

router = APIRouter()


@router.get("")
async def gallery_list(token_data: AccessTokenData = Depends(get_current_user)):
    controller = GalleryListController(token_data)
    return await controller.get_galleries()


@router.get("/{gallery_id}")
async def gallery_list(
    gallery_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    controller = GalleryDetailController(token_data, gallery_id)
    return await controller.get_gallery_detail()
