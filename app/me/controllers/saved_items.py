from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.items.bucket.models import ItemBucket
from app.items.vimeo.models import ItemVimeo
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType


class SavedItemsController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_saved_bucket_items(self) -> list[ItemBucket]:
        query = """SELECT
        i.*,
        source.title as source_title,
        source.bucket_name,
        source.media_prefix,
        source.grid_view
        FROM saved_item_bucket AS s
        LEFT JOIN item_bucket AS i ON i.id = s.item_bucket_id
        LEFT JOIN source_bucket AS source ON source.id = i.source_bucket_id 
        WHERE s.created_by_id = $1
        """
        values: tuple = (int(self.token_data.user_id),)
        results: list[Record] = await self.db.select_many(query, *values)
        output: list[ItemBucket] = []
        for row in results:
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
        return output

    async def get_saved_vimeo_items(self) -> list[ItemVimeo]:
        query = """SELECT i.* 
        FROM saved_item_vimeo AS s
        LEFT JOIN item_vimeo AS i ON i.id = s.item_vimeo_id 
        WHERE s.created_by_id = $1"""
        values: tuple = (int(self.token_data.user_id),)
        results: list[Record] = await self.db.select_many(query, *values)
        output: list[ItemVimeo] = []
        for row in results:
            item = ItemVimeo(**row)
            output.append(item)
        return output

    async def get_saved_items(self):
        return {
            "bucket": await self.get_saved_bucket_items(),
            "vimeo": await self.get_saved_vimeo_items(),
        }
