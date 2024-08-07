from fastapi import APIRouter

from app.public.gallery_links.controller import GalleryLinkController

router = APIRouter()


@router.get("/{link}")
async def gallery_link_detail(link: str):
    controller = GalleryLinkController(link)
    return await controller.get_gallery_link()
