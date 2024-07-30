from datetime import datetime, timezone

from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.sources.models import Source


class SourcesController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_list(self):
        return await self.db.select_many("SELECT * FROM source")


class SourceDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data)
        self.source_id = source_id

    async def source_detail(self):
        result: Record = await self.db.select_one(
            "SELECT * FROM source WHERE id = ($1)", self.source_id
        )
        if not result:
            raise HTTPException(status_code=404)
        return Source(
            id=result["id"],
            name=result["name"],
            bucket_name=result["bucket_name"],
            media_prefix=result["media_prefix"],
            grid_view=result["grid_view"],
        )


class SourceImportController(BaseController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data)
        self.source_id = source_id

    async def post_group(self, objects: list[dict]):
        output: list[dict] = []
        async with self.db.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    query = """INSERT INTO item
                    (source_id, 
                    mime_type, 
                    file_path, 
                    file_size, 
                    date_created, 
                    created_by)
                    VALUES ($1, $2, $3, $4, $5, $6) 
                    RETURNING *"""
                    for obj in objects:
                        values: tuple = (
                            self.source_id,
                            obj["mime_type"],
                            obj["key"],
                            obj["size"],
                            datetime.now(tz=timezone.utc),
                            "brando",
                        )
                        result = await connection.fetchrow(query, *values)
                        output.append(dict(result))
                    return output
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    async def import_from_source(self):
        record = await self.db.select_one(
            "SELECT * FROM source WHERE id = ($1)", self.source_id
        )
        bucket_name = record["bucket_name"]
        s3_client = self.get_s3_client(
            record["access_key_id"], record["secret_access_key"]
        )
        paginator = s3_client.get_paginator("list_objects_v2")

        output = []

        for page in paginator.paginate(Bucket=bucket_name):
            if "Contents" in page:
                for obj in page["Contents"]:
                    key = obj["Key"]
                    mime_type = self.get_mime_type(key)
                    obj_dict = {
                        "key": key,
                        "size": obj["Size"],
                        "mime_type": mime_type,
                    }
                    output.append(obj_dict)
        return await self.post_group(output)
