from fastapi import APIRouter

router = APIRouter()


@router.get("/{link}")
async def item_link_detail(link: str):
    return f"item link_detail {link}"
