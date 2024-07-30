from fastapi import APIRouter

from app.items.s3 import routes as s3

router = APIRouter()

router.include_router(s3.router, prefix="/s3")
