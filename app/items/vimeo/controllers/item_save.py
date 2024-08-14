from app.authentication.models import AccessTokenData
from app.items.item_links.controller import ItemLinkController


class ItemVimeoSaveController(ItemLinkController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data)
        self.item_id = item_id

    async def save_item(self):
        query = "INSERT INTO saved_item_vimeo (item_vimeo_id, created_by_id) VALUES ($1, $2) RETURNING id"
        values: tuple = (
            self.item_id,
            int(self.token_data.user_id),
        )
        await self.db.insert(query, *values)

    async def delete_saved_item(self):
        query = "DELETE FROM saved_item_vimeo WHERE item_vimeo_id = $1 AND created_by_id = $2"
        values: tuple = (
            self.item_id,
            int(self.token_data.user_id),
        )
        await self.db.delete_one(query, *values)
