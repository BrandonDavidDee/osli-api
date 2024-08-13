from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.galleries.models import Gallery
from app.users.models import User


class GalleryListController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def gallery_create(self, payload: Gallery):
        query = """INSERT INTO gallery 
        (title, view_type, description, created_by_id)
        VALUES ($1, $2, $3, $4) RETURNING *"""
        values: tuple = (
            payload.title,
            "grid",
            payload.description,
            int(self.token_data.user_id),
        )
        result: Record = await self.db.insert(query, *values)
        return result["id"]

    async def get_galleries(self) -> list[Gallery]:
        query = """SELECT 
        g.*,
        u.id as user_id,
        u.username,
        u.is_active as user_is_active
        FROM gallery AS g
        LEFT JOIN auth_user AS u ON u.id = g.created_by_id
        ORDER BY g.date_created DESC
        """
        results: list[Record] = await self.db.select_many(query)
        output: list[Gallery] = []
        for row in results:
            gallery = Gallery(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                date_created=row["date_created"],
                created_by=User(
                    id=row["user_id"],
                    username=row["username"],
                    is_active=row["user_is_active"],
                ),
            )
            output.append(gallery)
        return output
