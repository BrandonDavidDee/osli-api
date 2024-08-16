from app.authentication.models import AccessTokenData
from app.controller import BaseController


class MyLinksController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    @staticmethod
    async def get_gallery_links() -> list:
        return []

    @staticmethod
    async def get_item_links() -> list:
        return []

    async def get_links(self) -> dict:
        return {
            "gallery": await self.get_gallery_links(),
            "item": await self.get_item_links(),
        }
