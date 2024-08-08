from fastapi import APIRouter

from app.public.item_links.controller import PublicItemLinkController

router = APIRouter()


@router.get("/{link}")
async def item_link_detail(link: str):
    controller = PublicItemLinkController(link)
    return await controller.get_item_link()
