from app.authentication.models import AccessTokenData
from app.controller import BaseController


class MyLinksController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_gallery_links(self):
        pass

    async def get_item_links(self):
        pass

    async def get_links(self):
        return {
            "gallery": await self.get_gallery_links(),
            "item": await self.get_item_links(),
        }
