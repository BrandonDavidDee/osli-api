from fastapi import APIRouter

from app.public.gallery_links import routes as gallery_links
from app.public.item_links import routes as item_links

router = APIRouter()

router.include_router(gallery_links.router, prefix="/gallery")
router.include_router(item_links.router, prefix="/item")
