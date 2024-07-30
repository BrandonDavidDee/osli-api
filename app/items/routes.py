from fastapi import APIRouter

from app.items.s3 import routes as s3
from app.items.vimeo import routes as vimeo

router = APIRouter()

router.include_router(s3.router, prefix="/s3")
router.include_router(vimeo.router, prefix="/vimeo")
