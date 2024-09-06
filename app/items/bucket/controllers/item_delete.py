from app.authentication.models import AccessTokenData
from app.items.bucket.models import ItemBucket
from app.sources.bucket.controllers.s3_api import S3ApiController


class ItemBucketDeleteController(S3ApiController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)

    async def delete_item(
        self, encryption_key: str, item_id: int, payload: ItemBucket
    ) -> int:
        key = payload.file_path
        result: dict = await self.s3_object_delete(encryption_key, key)
        if result:
            query = "DELETE FROM item_bucket WHERE source_bucket_id = $1 AND id = $2 RETURNING *"
            values: tuple = (
                self.source_id,
                item_id,
            )
            await self.db.delete_one(query, values)
        return item_id
