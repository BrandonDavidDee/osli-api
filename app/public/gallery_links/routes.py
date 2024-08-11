from fastapi import APIRouter, BackgroundTasks

from app.public.gallery_links.controller import PublicGalleryLinkController

router = APIRouter()


@router.get("/{link}")
async def gallery_link_detail(link: str, bg_tasks: BackgroundTasks):
    controller = PublicGalleryLinkController(link)
    return await controller.get_gallery_link(bg_tasks)
