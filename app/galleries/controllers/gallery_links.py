import os

from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.galleries.models import Gallery, GalleryLink
from app.users.models import User


class GalleryLinkController(BaseController):
    def __init__(self, token_data: AccessTokenData, gallery_id: int):
        super().__init__(token_data)
        self.gallery_id = gallery_id
        self.site_url = os.getenv("SITE_URL")

    def make_public_url(self, link: str) -> str:
        base = self.site_url if self.site_url else "https://localhost:9000"
        return f"{base}/#/share/gallery/{link}"

    async def gallery_link_create(self, payload: GalleryLink):
        new_link = self.generate_link()
        print(new_link)
        query = """INSERT INTO gallery_link
        (gallery_id, title, link, expiration_date, date_created, created_by_id)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """
        values: tuple = (
            self.gallery_id,
            payload.title,
            new_link,
            payload.expiration_date,
            self.now,
            int(self.token_data.user_id),
        )
        await self.db.insert(query, *values)

    async def get_gallery_links(self):
        query = """SELECT 
        g.*,
        gl.id as link_id,
        gl.title as link_title,
        gl.link as link_link,
        gl.expiration_date as link_expiration_date,
        gl.view_count as link_view_count,
        gl.date_created as link_date_created,
        u.id as user_id,
        u.username,
        u.is_active as user_is_active
        FROM gallery AS g 
        LEFT JOIN gallery_link AS gl ON gl.gallery_id = g.id
        LEFT JOIN auth_user AS u ON u.id = gl.created_by_id
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
            gallery_link = GalleryLink(
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
        gallery.links = links

        return gallery

    async def gallery_link_update(self, gallery_link_id: int, payload: GalleryLink):
        query = "UPDATE gallery_link SET title = $1 WHERE id = $2 RETURNING *"
        values: tuple = (
            payload.title,
            gallery_link_id,
        )
        result: Record = await self.db.insert(query, *values)
        payload.title = result["title"]
        return payload

    async def gallery_link_delete(self, gallery_link_id: int):
        pass
