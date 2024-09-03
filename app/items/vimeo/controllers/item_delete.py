from app.authentication.models import AccessTokenData
from app.sources.vimeo.controllers.vimeo_api import VimeoApiController


class ItemVimeoDeleteController(VimeoApiController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)

    async def delete_item(self, item_id: int) -> int:
        query = (
            "DELETE FROM item_vimeo WHERE source_vimeo_id = $1 AND id = $2 RETURNING *"
        )
        values: tuple = (
            self.source_id,
            item_id,
        )
        await self.db.delete_one(query, values)
        return item_id
