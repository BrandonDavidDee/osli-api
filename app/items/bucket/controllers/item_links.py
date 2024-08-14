from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.items.bucket.models import ItemBucket
from app.items.item_links.controller import ItemLinkController
from app.items.models import ItemLink


class ItemBucketLinkController(ItemLinkController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data)
        self.item_id = item_id

    async def item_link_create(self, payload: ItemLink):
        new_link = self.generate_link()
        query = """INSERT INTO item_link
        (item_bucket_id, title, link, expiration_date, created_by_id, is_active)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """
        values: tuple = (
            self.item_id,
            payload.title,
            new_link,
            payload.expiration_date,
            int(self.token_data.user_id),
            payload.is_active,
        )
        return await self.db.insert(query, *values)

    async def get_item_links(self):
        query = """SELECT 
        i.*,
        il.id as link_id,
        il.title as link_title,
        il.link as link_link,
        il.expiration_date as link_expiration_date,
        il.view_count as link_view_count,
        il.date_created as link_date_created,
        il.is_active as link_is_active,
        u.id as user_id,
        u.username,
        u.is_active as user_is_active
        FROM item_bucket AS i 
        LEFT JOIN item_link AS il ON il.item_bucket_id = i.id
        LEFT JOIN auth_user AS u ON u.id = il.created_by_id
        WHERE i.id = $1"""
        result: list[Record] = await self.db.select_many(query, self.item_id)
        if not result:
            raise HTTPException(status_code=404)
        base_row: Record = result[0]
        item_bucket = ItemBucket(**base_row)
        item_bucket.links = self.assemble_links(result)
        return item_bucket
