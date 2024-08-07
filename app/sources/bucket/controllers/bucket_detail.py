from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType


class SourceBucketDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data)
        self.source_id = source_id

    async def source_detail(self):
        result: Record = await self.db.select_one(
            "SELECT * FROM source_bucket WHERE id = ($1)", self.source_id
        )
        if not result:
            raise HTTPException(status_code=404)
        return SourceBucket(
            id=result["id"],
            source_type=SourceType.BUCKET,
            title=result["title"],
            bucket_name=result["bucket_name"],
            media_prefix=result["media_prefix"],
            grid_view=result["grid_view"],
        )
