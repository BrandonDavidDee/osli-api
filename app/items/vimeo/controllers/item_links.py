from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.items.item_links.controller import ItemLinkController
from app.items.models import ItemLink
from app.items.vimeo.models import ItemVimeo


class ItemVimeoLinkController(ItemLinkController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data, item_id)

    async def item_link_create(self, payload: ItemLink):
        new_link = self.generate_link()
        query = """INSERT INTO item_link
        (item_vimeo_id, title, link, expiration_date, date_created, created_by_id, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *
        """
        values: tuple = (
            self.item_id,
            payload.title,
            new_link,
            payload.expiration_date,
            self.now,
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
        FROM item_vimeo AS i 
        LEFT JOIN item_link AS il ON il.item_vimeo_id = i.id
        LEFT JOIN auth_user AS u ON u.id = il.created_by_id
        WHERE i.id = $1"""
        result: list[Record] = await self.db.select_many(query, self.item_id)
        if not result:
            raise HTTPException(status_code=404)
        base_row: Record = result[0]
        item_vimeo = ItemVimeo(**base_row)
        item_vimeo.links = self.assemble_links(result)
        return item_vimeo
