from app.authentication.models import AccessTokenData
from app.controller import BaseController


class MyGalleriesController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_my_galleries(self) -> None:
        pass
