from fastapi import APIRouter
from app.gallery_links.controller import GalleryLinkController

router = APIRouter()


@router.get("/{link}")
async def gallery_list(link: str):
    controller = GalleryLinkController(link)
    return await controller.get_gallery_link()
