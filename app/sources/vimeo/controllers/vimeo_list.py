from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.sources.models import SourceType
from app.sources.vimeo.models import SourceVimeo


class SourcesVimeoListController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_list(self) -> list[SourceVimeo]:
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
