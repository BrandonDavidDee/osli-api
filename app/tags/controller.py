from asyncpg import Record

from app.controller import BaseController
from app.tags.models import Tag
from app.authentication.models import AccessTokenData


class TagController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_list(self):
        result: list[Record] = await self.db.select_many("SELECT * FROM tag")
        output: list[Tag] = []
        for record in result:
            output.append(Tag(**record))
        return output
