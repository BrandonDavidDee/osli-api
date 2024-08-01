from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.sources.models import SourceType
from app.sources.vimeo.models import SourceVimeo


class SourcesVimeoController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_list(self):
        results: list[Record] = await self.db.select_many("SELECT * FROM source_vimeo")
        output: list[SourceVimeo] = []
        for row in results:
            output.append(
                SourceVimeo(
                    id=row["id"],
                    source_type=SourceType.VIMEO,
                    title=row["title"],
                    client_identifier=row["client_identifier"],
                    client_secret=row["client_secret"],
                    access_token=row["access_token"],
                    grid_view=row["grid_view"],
                )
            )
        return output


class SourceVimeoDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data)
        self.source_vimeo_id = source_id

    async def source_detail(self):
        result: Record = await self.db.select_one(
            "SELECT * FROM source_vimeo WHERE id = ($1)", self.source_vimeo_id
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
