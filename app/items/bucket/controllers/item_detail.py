from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.galleries.models import Gallery
from app.items.bucket.models import ItemBucket
from app.items.models import ItemTag
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType
from app.tags.models import Tag


class ItemBucketDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, source_id: int, item_id: int):
        super().__init__(token_data)
        self.source_id = source_id
        self.item_id = item_id

    async def item_detail(self) -> ItemBucket:
        query = """SELECT 
        i.*,
        sib.id as saved_item_id,
        source.title as source_title,
        source.bucket_name,
        source.media_prefix,
        source.grid_view,
        j.id as tag_item_id,
        tag.id as tag_id,
        tag.title as tag_title
        FROM item_bucket i 
        LEFT JOIN saved_item_bucket sib ON sib.item_bucket_id = i.id AND sib.created_by_id = $1
        LEFT JOIN source_bucket AS source ON source.id = i.source_bucket_id
        LEFT JOIN tag_item_bucket as j ON j.item_bucket_id = i.id
        LEFT JOIN tag ON tag.id = j.tag_id
        WHERE i.source_bucket_id = $2 AND i.id = $3
        """
        values: tuple = (
            self.created_by_id,
            self.source_id,
            self.item_id,
        )
        result: Record = await self.db.select_many(query, values)

        if not result:
            raise HTTPException(status_code=404)

        base_row = result[0]
        is_saved = bool(base_row["saved_item_id"])

        item = ItemBucket(**base_row)
        item.saved = is_saved
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

    async def item_update(self, payload: ItemBucket) -> ItemBucket:
        query = (
            "UPDATE item_bucket SET title = $1, notes = $2 WHERE id = $3 RETURNING *"
        )
        values: tuple = (
            payload.title,
            payload.notes,
            self.item_id,
        )
        await self.db.insert(query, values)
        return payload

    async def get_related(self) -> dict:
        galleries = await self._get_related_gallery_items()
        saved_users = await self._get_related_saved_items()
        has_related: bool = bool(len(galleries)) or bool(len(saved_users))
        return {
            "has_related": has_related,
            "galleries": galleries,
            "saved_users": saved_users,
        }

    async def _get_related_gallery_items(self) -> list[Gallery]:
        query = """SELECT g.*
        FROM gallery_item gi
        LEFT JOIN gallery g ON g.id = gi.gallery_id 
        WHERE gi.item_bucket_id = $1
        ORDER BY g.date_created DESC
        """
        values: tuple = (self.item_id,)
        results: list[Record] = await self.db.select_many(query, values)
        output: list[Gallery] = []
        seen_galleries = {}
        for row in results:
            gallery_id = row["id"]
            if gallery_id not in seen_galleries:
                gallery = Gallery(
                    id=gallery_id,
                    title=row["title"],
                    date_created=row["date_created"],
                )
                seen_galleries[gallery_id] = gallery
                output.append(gallery)
        return output

    async def _get_related_saved_items(self) -> list[str]:
        query = """SELECT u.username 
        FROM saved_item_bucket sib
        LEFT JOIN auth_user u ON u.id = sib.created_by_id
        WHERE sib.item_bucket_id = $1"""
        values: tuple = (self.item_id,)
        results: list[Record] = await self.db.select_many(query, values)
        output: list[str] = []
        for row in results:
            username = row["username"]
            if username not in output:
                output.append(username)
        return output
