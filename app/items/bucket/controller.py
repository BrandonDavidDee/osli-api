from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.items.bucket.models import ItemBucket, ItemTag
from app.items.models import SearchParams
from app.sources.bucket.controller import SourceBucketDetailController
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType
from app.tags.models import Tag


class ItemBucketListController(SourceBucketDetailController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)

    async def item_search(self, payload: SearchParams) -> dict:
        if len(payload.tag_ids):
            query = """SELECT
            count(*) OVER () AS total_count,
            i.*,
            sc.title as source_title,
            sc.bucket_name,
            sc.media_prefix,
            sc.grid_view
            FROM item_bucket AS i
            LEFT JOIN source_bucket AS sc ON sc.id = i.source_bucket_id
            LEFT JOIN tag_item_bucket as j ON j.item_bucket_id = i.id """
            placeholders = ", ".join(
                f"${i}" for i in range(7, 7 + len(payload.tag_ids))
            )
            query += f""" WHERE 
            (
              ($3 = '') OR (i.notes ILIKE '%' || $4 || '%') OR (i.file_path ILIKE '%' || $5 || '%')
            ) 
            AND j.tag_id IN ({placeholders})
            AND i.source_bucket_id = $6
            """
            query += """ 
            GROUP BY i.id, sc.title, sc.bucket_name, sc.media_prefix, sc.grid_view
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            values: tuple = (
                payload.limit,
                payload.offset,
                payload.filter,
                payload.filter,
                payload.filter,
                self.source_id,
            )
            combined_values: tuple = values + tuple(payload.tag_ids)
            result: Record = await self.db.select_many(query, *combined_values)
        else:
            query = """SELECT
            count(*) OVER () AS total_count,
            i.*,
            sc.title as source_title,
            sc.bucket_name,
            sc.media_prefix,
            sc.grid_view
            FROM item_bucket AS i
            LEFT JOIN source_bucket AS sc ON sc.id = i.source_bucket_id
            WHERE (($3 = '') OR i.notes ILIKE '%' || $4 || '%' OR i.file_path ILIKE '%' || $5 || '%')
            AND i.source_bucket_id = $6
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            values: tuple = (
                payload.limit,
                payload.offset,
                payload.filter,
                payload.filter,
                payload.filter,
                self.source_id,
            )
            result: Record = await self.db.select_many(query, *values)

        output: list[ItemBucket] = []

        for row in result:
            item = ItemBucket(**row)
            if row["source_bucket_id"]:
                item.source = SourceBucket(
                    id=row["source_bucket_id"],
                    title=row["source_title"],
                    bucket_name=row["bucket_name"],
                    media_prefix=row["media_prefix"],
                    grid_view=row["grid_view"],
                    source_type=SourceType.BUCKET,
                )
            item.file_name = self.get_filename(row["file_path"])
            output.append(item)
        total_count = result[0]["total_count"] if result else 0

        if output:
            # we've joined the source to each item:
            source = output[0].source
        else:
            # but if there are no results, we still want the list view page to have source info:
            source = await self.source_detail()

        return {
            "source": source,
            "total_count": total_count,
            "items": output,
        }


class ItemBucketDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data)
        self.item_id = item_id

    async def item_detail(self):
        query = """SELECT 
        i.*,
        sc.title as source_title,
        sc.bucket_name,
        sc.media_prefix,
        sc.grid_view,
        j.id as tag_item_id,
        tag.id as tag_id,
        tag.title as tag_title
        FROM item_bucket i 
        LEFT JOIN source_bucket AS sc ON sc.id = i.source_bucket_id
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
        query = "UPDATE item_bucket SET notes = $1 WHERE id = $2 RETURNING *"
        values: tuple = (
            payload.notes,
            self.item_id,
        )
        await self.db.insert(query, *values)
        return payload
