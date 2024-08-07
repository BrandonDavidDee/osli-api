from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType


class SourceBucketListController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_list(self) -> list[SourceBucket]:
        results: list[Record] = await self.db.select_many("SELECT * FROM source_bucket")
        output: list[SourceBucket] = []
        for row in results:
            output.append(
                SourceBucket(
                    id=row["id"],
                    source_type=SourceType.BUCKET,
                    title=row["title"],
                    bucket_name=row["bucket_name"],
                    media_prefix=row["media_prefix"],
                    grid_view=row["grid_view"],
                )
            )
        return output
