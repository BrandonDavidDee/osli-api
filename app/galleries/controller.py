from app.controller import BaseController
from app.authentication.models import AccessTokenData
from fastapi import HTTPException


class GalleryListController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_galleries(self):
        query = "SELECT * FROM gallery"
        return await self.db.select_many(query)


class GalleryDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, gallery_id: int):
        super().__init__(token_data)
        self.gallery_id = gallery_id

    async def get_gallery_detail(self):
        query = "SELECT * FROM gallery WHERE id = $1"
        result = await self.db.select_one(query, self.gallery_id)
        # if self.token_data.username != result['created_by']:
        #     raise HTTPException(status_code=404)
        return result
