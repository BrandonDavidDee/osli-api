import os

from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.items.models import ItemLink
from app.users.models import User


class ItemLinkController(BaseController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data)
        self.item_id = item_id
        self.site_url = os.getenv("SITE_URL")

    def assemble_item_link(self, row: Record) -> ItemLink:
        view_count = row["link_view_count"] if row["link_view_count"] else 0
        link = self.make_public_url(row["link_link"])
        return ItemLink(
            id=row["link_id"],
            title=row["link_title"],
            link=link,
            expiration_date=row["link_expiration_date"],
            is_active=bool(row["link_is_active"]),
            view_count=view_count,
            date_created=row["link_date_created"],
            created_by=User(
                id=row["user_id"],
                username=row["username"],
                is_active=row["user_is_active"],
            ),
        )

    def assemble_links(self, result: list[Record]) -> list[ItemLink]:
        output: list[ItemLink] = []
        for row in result:
            if row["link_id"]:
                item_link = self.assemble_item_link(row)
                output.append(item_link)
        output.sort(key=lambda x: x.date_created, reverse=True)
        return output

    def make_public_url(self, link: str) -> str:
        base = self.site_url if self.site_url else "https://localhost:9000"
        return f"{base}/#/share/item/{link}"

    async def item_link_update(self, item_link_id: int, payload: ItemLink):
        query = (
            "UPDATE item_link SET title = $1, is_active = $2 WHERE id = $3 RETURNING *"
        )
        values: tuple = (
            payload.title,
            payload.is_active,
            item_link_id,
        )
        result: Record = await self.db.insert(query, *values)
        payload.title = result["title"]
        return payload

    async def item_link_delete(self, item_link_id: int):
        pass
