from app.authentication.models import AccessTokenData
from app.items.item_links.controller import ItemLinkController


class ItemBucketSaveController(ItemLinkController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data)
        self.item_id = item_id

    async def save_item(self) -> None:
        query = "INSERT INTO saved_item_bucket (item_bucket_id, created_by_id) VALUES ($1, $2) RETURNING id"
        values: tuple = (
            self.item_id,
            self.created_by_id,
        )
        await self.db.insert(query, values)

    async def delete_saved_item(self) -> None:
        query = "DELETE FROM saved_item_bucket WHERE item_bucket_id = $1 AND created_by_id = $2"
        values: tuple = (
            self.item_id,
            self.created_by_id,
        )
        await self.db.delete_one(query, values)
