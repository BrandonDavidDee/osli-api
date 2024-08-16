from fastapi import APIRouter, BackgroundTasks

from app.public.item_links.controller import PublicItemLinkController
from app.public.item_links.models import PublicItemLink

router = APIRouter()


@router.get("/{link}")
async def item_link_detail(link: str, bg_tasks: BackgroundTasks) -> PublicItemLink:
    controller = PublicItemLinkController(link)
    return await controller.get_item_link(bg_tasks)
