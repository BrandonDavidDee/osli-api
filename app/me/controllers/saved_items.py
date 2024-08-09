from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController


class SavedItemsController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_saved_bucket_items(self):
        query = "SELECT * FROM saved_item_bucket WHERE created_by_id = $1"
        values: tuple = (int(self.token_data.user_id),)
        results: list[Record] = await self.db.select_many(query, *values)
        return results

    async def get_saved_vimeo_items(self):
        query = "SELECT * FROM saved_item_vimeo WHERE created_by_id = $1"
        values: tuple = (int(self.token_data.user_id),)
        results: list[Record] = await self.db.select_many(query, *values)
        return results

    async def get_saved_items(self):
        return {
            "bucket": await self.get_saved_bucket_items(),
            "vimeo": await self.get_saved_vimeo_items(),
        }
