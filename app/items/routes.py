from fastapi import APIRouter

from app.items.bucket import routes as bucket
from app.items.vimeo import routes as vimeo

router = APIRouter()

router.include_router(bucket.router, prefix="/bucket")
router.include_router(vimeo.router, prefix="/vimeo")
