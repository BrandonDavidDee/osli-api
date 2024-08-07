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

    async def gallery_link_create(self):
        pass

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
            gallery_link = GalleryLink(
                id=row["link_id"],
                title=row["link_title"],
                link=row["link_link"],
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

    async def gallery_link_update(self, gallery_link_id: int):
        pass

    async def gallery_link_delete(self, gallery_link_id: int):
        pass
