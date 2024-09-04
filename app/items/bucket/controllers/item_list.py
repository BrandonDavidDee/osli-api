from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.items.bucket.models import ItemBucket
from app.items.models import SearchParams
from app.sources.bucket.controllers.bucket_detail import SourceBucketDetailController
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType


class ItemBucketListController(SourceBucketDetailController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)

    async def item_search(self, payload: SearchParams) -> dict:
        if len(payload.tag_ids):
            query = """SELECT
            count(*) OVER () AS total_count,
            i.*,
            source.title as source_title,
            source.bucket_name,
            source.media_prefix,
            source.grid_view
            FROM item_bucket AS i
            LEFT JOIN source_bucket AS source ON source.id = i.source_bucket_id
            LEFT JOIN tag_item_bucket as j ON j.item_bucket_id = i.id """
            placeholders = ", ".join(
                f"${i}" for i in range(8, 8 + len(payload.tag_ids))
            )
            query += f""" WHERE 
            (
              ($3 = '') 
              OR (i.notes ILIKE '%' || $4 || '%') 
              OR (i.file_path ILIKE '%' || $5 || '%')
              OR (i.title ILIKE '%' || $6 || '%')
            ) 
            AND j.tag_id IN ({placeholders})
            AND i.source_bucket_id = $7
            """
            query += """ 
            GROUP BY i.id, source.title, source.bucket_name, source.media_prefix, source.grid_view
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            values: tuple = (
                payload.limit,
                payload.offset,
                payload.filter,
                payload.filter,
                payload.filter,
                payload.filter,
                self.source_id,
            )
            combined_values: tuple = values + tuple(payload.tag_ids)
            result: Record = await self.db.select_many(query, combined_values)
        else:
            query = """SELECT
            count(*) OVER () AS total_count,
            i.*,
            source.title as source_title,
            source.bucket_name,
            source.media_prefix,
            source.grid_view
            FROM item_bucket AS i
            LEFT JOIN source_bucket AS source ON source.id = i.source_bucket_id
            WHERE (
            ($3 = '') 
            OR (i.notes ILIKE '%' || $4 || '%') 
            OR (i.file_path ILIKE '%' || $5 || '%')
            OR (i.title ILIKE '%' || $6 || '%')
            )
            AND i.source_bucket_id = $7
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            values = (
                payload.limit,
                payload.offset,
                payload.filter,
                payload.filter,
                payload.filter,
                payload.filter,
                self.source_id,
            )
            result = await self.db.select_many(query, values)

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
