from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.sources.bucket.controllers.s3_api import S3ApiController
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType


class SourceBucketDetailController(S3ApiController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)
        self.source_id = source_id

    async def source_create(self):
        pass

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

    async def source_update(self, passphrase: str, payload: SourceBucket) -> int:
        query = """UPDATE source_bucket SET
        title = $1,
        bucket_name = $2,
        access_key_id = $3,
        secret_access_key = $4,
        media_prefix = $5,
        grid_view = $6
        WHERE id = $7 RETURNING *"""
        encrypted_access_key_id = self.encryption.encrypt_api_key(
            payload.access_key_id, passphrase
        )
        encrypted_secret_access_key = self.encryption.encrypt_api_secret(
            payload.secret_access_key, passphrase
        )
        values: tuple = (
            payload.title,
            payload.bucket_name,
            encrypted_access_key_id,
            encrypted_secret_access_key,
            payload.media_prefix,
            payload.grid_view,
            self.source_id,
        )
        result: Record = await self.db.insert(query, *values)
        return result["id"]
