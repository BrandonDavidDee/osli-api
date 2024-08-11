from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.items.bucket.models import ItemBucket
from app.items.vimeo.models import ItemVimeo
from app.me.models import SavedItem
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType
from app.sources.vimeo.models import SourceVimeo


class SavedItemsController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_saved_bucket_items(self) -> list[Record]:
        query = """SELECT i.*,
        s.date_created as date_saved,
        source.title as source_title,
        source.bucket_name,
        source.media_prefix,
        source.grid_view
        FROM saved_item_bucket AS s
        LEFT JOIN item_bucket AS i ON i.id = s.item_bucket_id
        LEFT JOIN source_bucket AS source ON source.id = i.source_bucket_id 
        WHERE s.created_by_id = $1
        ORDER BY s.date_created DESC"""
        values: tuple = (int(self.token_data.user_id),)
        results: list[Record] = await self.db.select_many(query, *values)
        return results

    async def get_saved_vimeo_items(self) -> list[Record]:
        query = """SELECT i.*,
        s.date_created as date_saved,
        source.title as source_title,
        source.client_identifier,
        source.client_secret,
        source.access_token,
        source.grid_view
        FROM saved_item_vimeo AS s
        LEFT JOIN item_vimeo AS i ON i.id = s.item_vimeo_id
        LEFT JOIN source_vimeo AS source ON source.id = i.source_vimeo_id 
        WHERE s.created_by_id = $1
        ORDER BY s.date_created DESC"""
        values: tuple = (int(self.token_data.user_id),)
        results: list[Record] = await self.db.select_many(query, *values)
        return results

    async def get_saved_items(self):
        items_bucket: list[Record] = await self.get_saved_bucket_items()
        items_vimeo: list[Record] = await self.get_saved_vimeo_items()
        output: list[SavedItem] = []

        for row in items_bucket:
            item_bucket = ItemBucket(**row)
            if row["source_bucket_id"]:
                item_bucket.source = SourceBucket(
                    id=row["source_bucket_id"],
                    title=row["source_title"],
                    bucket_name=row["bucket_name"],
                    media_prefix=row["media_prefix"],
                    grid_view=row["grid_view"],
                    source_type=SourceType.BUCKET,
                )
            item_bucket.file_name = self.get_filename(row["file_path"])
            saved_item = SavedItem(
                source_type=SourceType.VIMEO,
                item_bucket=item_bucket,
                date_saved=row["date_saved"],
            )
            output.append(saved_item)

        for row in items_vimeo:
            item_vimeo = ItemVimeo(**row)
            item_vimeo.source = SourceVimeo(
                id=row["source_vimeo_id"],
                title=row["source_title"],
                client_identifier=row["client_identifier"],
                client_secret=row["client_secret"],
                access_token=row["access_token"],
                grid_view=row["grid_view"],
                source_type=SourceType.BUCKET,
            )
            saved_item = SavedItem(
                source_type=SourceType.VIMEO,
                item_vimeo=item_vimeo,
                date_saved=row["date_saved"],
            )
            output.append(saved_item)

        output.sort(key=lambda x: x.date_saved, reverse=True)
        return output
