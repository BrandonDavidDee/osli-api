from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.items.bucket.models import ItemBucket
from app.items.models import ItemTag
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType
from app.tags.models import Tag


class ItemBucketDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data)
        self.item_id = item_id

    async def item_detail(self):
        query = """SELECT 
        i.*,
        source.title as source_title,
        source.bucket_name,
        source.media_prefix,
        source.grid_view,
        j.id as tag_item_id,
        tag.id as tag_id,
        tag.title as tag_title
        FROM item_bucket i 
        LEFT JOIN source_bucket AS source ON source.id = i.source_bucket_id
        LEFT JOIN tag_item_bucket as j ON j.item_bucket_id = i.id
        LEFT JOIN tag ON tag.id = j.tag_id
        WHERE i.id = $1
        """
        values: tuple = (self.item_id,)
        result: Record = await self.db.select_many(query, *values)

        if not result:
            raise HTTPException(status_code=404)

        base_row = result[0]

        item = ItemBucket(**base_row)
        item.source = SourceBucket(
            id=base_row["source_bucket_id"],
            title=base_row["source_title"],
            bucket_name=base_row["bucket_name"],
            media_prefix=base_row["media_prefix"],
            grid_view=base_row["grid_view"],
            source_type=SourceType.BUCKET,
        )

        for record in result:
            if record["tag_item_id"]:
                item_tag = ItemTag(
                    id=record["tag_item_id"],
                    tag=Tag(id=record["tag_id"], title=record["tag_title"]),
                )
                item.tags.append(item_tag)

        return item

    async def item_update(self, payload: ItemBucket):
        query = (
            "UPDATE item_bucket SET title = $1, notes = $2 WHERE id = $3 RETURNING *"
        )
        values: tuple = (
            payload.title,
            payload.notes,
            self.item_id,
        )
        await self.db.insert(query, *values)
        return payload
