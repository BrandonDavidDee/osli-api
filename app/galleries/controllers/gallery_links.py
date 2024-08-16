import os
from datetime import datetime

from asyncpg import Record
from fastapi import HTTPException, Response

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.galleries.models import Gallery, GalleryLink
from app.users.models import User


class GalleryLinkUpdateController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)
        self.site_url = os.getenv("SITE_URL")

    def make_public_url(self, link: str) -> str:
        base = self.site_url if self.site_url else "https://localhost:9000"
        return f"{base}/#/share/gallery/{link}"

    async def link_availability(self, link: str) -> bool:
        query = "SELECT * FROM gallery_link WHERE link = $1"
        result: Record = await self.db.select_one(query, link)
        return bool(result)

    async def link_only_update(
        self, gallery_link_id: int, payload: GalleryLink
    ) -> GalleryLink:
        query = "UPDATE gallery_link SET link = $1 WHERE id = $2 RETURNING link"
        values: tuple = (
            payload.link,
            gallery_link_id,
        )
        result = await self.db.insert(query, values)
        payload.link = self.make_public_url(result["link"])
        return payload


class GalleryLinkController(GalleryLinkUpdateController):
    def __init__(self, token_data: AccessTokenData, gallery_id: int) -> None:
        super().__init__(token_data)
        self.gallery_id = gallery_id

    async def gallery_link_create(self, payload: GalleryLink) -> int:
        new_link = self.generate_link()
        query = """INSERT INTO gallery_link
        (gallery_id, title, link, is_active, expiration_date, created_by_id)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """
        values: tuple = (
            self.gallery_id,
            payload.title,
            new_link,
            payload.is_active,
            payload.expiration_date,
            self.created_by_id,
        )
        result = await self.db.insert(query, values)
        inserted_id: int = result["id"]
        return inserted_id

    async def get_gallery_links(self) -> Gallery:
        query = """SELECT 
        g.*,
        
        u.id as user_id,
        u.username,
        u.is_active as user_is_active,
        
        gl.id as link_id,
        gl.title as link_title,
        gl.link as link_link,
        gl.expiration_date as link_expiration_date,
        gl.view_count as link_view_count,
        gl.date_created as link_date_created,
        gl.is_active as link_is_active,
        
        lu.id as link_user_id,
        lu.username as link_username,
        lu.is_active as link_user_is_active
        
        FROM gallery AS g 
        LEFT JOIN auth_user AS u ON u.id = g.created_by_id
        LEFT JOIN gallery_link AS gl ON gl.gallery_id = g.id
        LEFT JOIN auth_user AS lu ON lu.id = gl.created_by_id
        WHERE g.id = $1"""
        result: list[Record] = await self.db.select_many(query, self.gallery_id)
        if not result:
            raise HTTPException(status_code=404)
        base_row: Record = result[0]
        gallery = Gallery(
            id=base_row["id"],
            title=base_row["title"],
            description=base_row["description"],
            date_created=base_row["date_created"],
            created_by=User(
                id=base_row["user_id"],
                username=base_row["username"],
                is_active=base_row["user_is_active"],
            ),
        )
        links: list[GalleryLink] = []
        for row in result:
            view_count = row["link_view_count"] if row["link_view_count"] else 0
            link = self.make_public_url(row["link_link"])
            if row["link_id"]:
                gallery_link = GalleryLink(
                    id=row["link_id"],
                    title=row["link_title"],
                    link=link,
                    expiration_date=row["link_expiration_date"],
                    view_count=view_count,
                    is_active=bool(row["link_is_active"]),
                    date_created=row["link_date_created"],
                    created_by=User(
                        id=row["link_user_id"],
                        username=row["link_username"],
                        is_active=row["link_user_is_active"],
                    ),
                )
                links.append(gallery_link)
        # links.sort(key=lambda x: x.date_created, reverse=True)
        links.sort(key=lambda x: x.date_created or datetime.min, reverse=True)
        gallery.links = links

        return gallery

    async def gallery_link_update(
        self, gallery_link_id: int, payload: GalleryLink
    ) -> GalleryLink:
        query = "UPDATE gallery_link SET title = $1, is_active = $2 WHERE id = $3 RETURNING *"
        values: tuple = (
            payload.title,
            payload.is_active,
            gallery_link_id,
        )
        result: Record = await self.db.insert(query, values)
        payload.title = result["title"]
        return payload

    async def gallery_link_delete(self, gallery_link_id: int) -> Response:
        query = "DELETE FROM gallery_link WHERE id = $1"
        values: tuple = (gallery_link_id,)
        return await self.db.delete_one(query, values)
