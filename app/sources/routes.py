from fastapi import APIRouter

from app.sources.bucket import routes as bucket
from app.sources.vimeo import routes as vimeo

router = APIRouter()

router.include_router(bucket.router, prefix="/bucket")
router.include_router(vimeo.router, prefix="/vimeo")
