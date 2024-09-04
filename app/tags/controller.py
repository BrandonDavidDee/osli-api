from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.tags.models import Tag


class TagController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def tag_create(self, payload: Tag) -> Tag:
        query = "INSERT INTO tag (title) VALUES ($1) RETURNING *"
        title = payload.title.strip()
        result: Record = await self.db.insert(query, (title,))
        inserted_id: int = result["id"]
        payload.id = inserted_id
        return payload

    async def get_list(self) -> list[Tag]:
        result: list[Record] = await self.db.select_many("SELECT * FROM tag")
        output: list[Tag] = []
        for record in result:
            output.append(Tag(**record))
        return output

    async def tag_update(self, tag_id: int, payload: Tag) -> Tag:
        query = "UPDATE tag SET title = $1 WHERE id = $2 RETURNING *"
        title = payload.title.strip()
        values: tuple = (
            title,
            tag_id,
        )
        await self.db.insert(query, values)
        return payload

    async def _get_bucket_tag_count(self, tag_id: int) -> int:
        query = "SELECT count(*) FROM tag_item_bucket WHERE item_bucket_id = $1"
        result: Record = await self.db.select_many(query, (tag_id,))
        count: int = result["count"]
        return count

    async def _get_vimeo_tag_count(self, tag_id: int) -> int:
        query = "SELECT count(*) FROM tag_item_vimeo WHERE item_vimeo_id = $1"
        result: Record = await self.db.select_many(query, (tag_id,))
        count: int = result["count"]
        return count

    async def tag_related(self, tag_id: int) -> int:
        related_bucket: int = await self._get_bucket_tag_count(tag_id)
        related_vimeo: int = await self._get_vimeo_tag_count(tag_id)
        return related_bucket + related_vimeo

    async def tag_delete(self, tag_id: int) -> int:
        query = "DELETE FROM tag WHERE id = $1"
        await self.db.delete_one(query, (tag_id,))
        return tag_id
