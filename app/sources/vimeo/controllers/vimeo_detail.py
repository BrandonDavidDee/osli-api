from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.sources.models import SourceType
from app.sources.vimeo.models import SourceVimeo


class SourceVimeoDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data)
        self.source_id = source_id

    async def source_detail(self):
        result: Record = await self.db.select_one(
            "SELECT * FROM source_vimeo WHERE id = ($1)", self.source_id
        )
        if not result:
            raise HTTPException(status_code=404)
        return SourceVimeo(
            id=result["id"],
            source_type=SourceType.VIMEO,
            title=result["title"],
            client_identifier=result["client_identifier"],
            client_secret=result["client_secret"],
            access_token=result["access_token"],
            grid_view=result["grid_view"],
        )
