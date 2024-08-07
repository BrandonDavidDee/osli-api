import os

from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.items.bucket.models import ItemBucket
from app.items.models import ItemLink
from app.items.vimeo.models import ItemVimeo
from app.sources.models import SourceType
from app.users.models import User


class ItemLinkController(BaseController):
    def __init__(
        self, token_data: AccessTokenData, source_type: SourceType, item_id: int
    ):
        super().__init__(token_data)
        self.source_type = source_type
        self.item_id = item_id
        self.site_url = os.getenv("SITE_URL")

    def make_public_url(self, link: str) -> str:
        base = self.site_url if self.site_url else "https://localhost:9000"
        return f"{base}/#/share/item/{link}"

    async def item_link_create(self, payload: ItemLink):
        new_link = self.generate_link()
        if self.source_type == SourceType.BUCKET:
            query = """INSERT INTO item_link
            (item_bucket_id, title, link, expiration_date, date_created, created_by_id)
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
            """
        elif self.source_type == SourceType.VIMEO:
            query = """INSERT INTO item_link
            (item_vimeo_id, title, link, expiration_date, date_created, created_by_id)
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
            """
        else:
            raise HTTPException(status_code=500, detail="Invalid source type")
        values: tuple = (
            self.item_id,
            payload.title,
            new_link,
            payload.expiration_date,
            self.now,
            int(self.token_data.user_id),
        )
        await self.db.insert(query, *values)

    async def get_item_bucket_links(self):
        query = """SELECT 
        i.*,
        il.id as link_id,
        il.title as link_title,
        il.link as link_link,
        il.expiration_date as link_expiration_date,
        il.view_count as link_view_count,
        il.date_created as link_date_created,
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

        links: list[ItemLink] = []
        for row in result:
            if row["link_id"]:
                view_count = row["link_view_count"] if row["link_view_count"] else 0
                link = self.make_public_url(row["link_link"])
                gallery_link = ItemLink(
                    id=row["link_id"],
                    title=row["link_title"],
                    link=link,
                    expiration_date=row["link_expiration_date"],
                    view_count=view_count,
                    date_created=row["link_date_created"],
                    created_by=User(
                        id=row["user_id"],
                        username=row["username"],
                        is_active=row["user_is_active"],
                    ),
                )
                links.append(gallery_link)
        links.sort(key=lambda x: x.date_created, reverse=True)
        item_bucket.links = links

        return item_bucket

    async def get_item_vimeo_links(self):
        query = """SELECT 
        i.*,
        il.id as link_id,
        il.title as link_title,
        il.link as link_link,
        il.expiration_date as link_expiration_date,
        il.view_count as link_view_count,
        il.date_created as link_date_created,
        u.id as user_id,
        u.username,
        u.is_active as user_is_active
        FROM item_vimeo AS i 
        LEFT JOIN item_link AS il ON il.item_bucket_id = i.id
        LEFT JOIN auth_user AS u ON u.id = il.created_by_id
        WHERE i.id = $1"""
        result: list[Record] = await self.db.select_many(query, self.item_id)
        if not result:
            raise HTTPException(status_code=404)
        base_row: Record = result[0]
        item_vimeo = ItemVimeo(**base_row)

        links: list[ItemLink] = []
        for row in result:
            if row["link_id"]:
                view_count = row["link_view_count"] if row["link_view_count"] else 0
                link = self.make_public_url(row["link_link"])
                gallery_link = ItemLink(
                    id=row["link_id"],
                    title=row["link_title"],
                    link=link,
                    expiration_date=row["link_expiration_date"],
                    view_count=view_count,
                    date_created=row["link_date_created"],
                    created_by=User(
                        id=row["user_id"],
                        username=row["username"],
                        is_active=row["user_is_active"],
                    ),
                )
                links.append(gallery_link)
        links.sort(key=lambda x: x.date_created, reverse=True)
        item_vimeo.links = links

        return item_vimeo

    async def item_link_update(self, item_link_id: int, payload: ItemLink):
        query = "UPDATE item_link SET title = $1 WHERE id = $2 RETURNING *"
        values: tuple = (
            payload.title,
            item_link_id,
        )
        result: Record = await self.db.insert(query, *values)
        payload.title = result["title"]
        return payload

    async def item_link_delete(self, item_link_id: int):
        pass
