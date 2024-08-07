from asyncpg import Record
from fastapi import Response

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.items.models import ItemTag


class ItemVimeoTagsController(BaseController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data)
        self.item_id = item_id

    async def item_tag_create(self, payload: ItemTag) -> ItemTag:
        query = "INSERT INTO tag_item_vimeo (tag_id, item_vimeo_id) VALUES ($1, $2) RETURNING id"
        values: tuple = (
            payload.tag.id,
            self.item_id,
        )
        result: Record = await self.db.insert(query, *values)
        payload.id = result["id"]
        return payload

    async def item_tag_delete(self, tag_item_vimeo_id: int) -> Response:
        query = "DELETE FROM tag_item_vimeo WHERE id = $1"
        return await self.db.delete_one(query, tag_item_vimeo_id)
