import boto3
from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController, KeyEncryptionController


class S3ApiController(BaseController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data)
        self.source_id = source_id
        self.s3_client = None
        self.encryption = KeyEncryptionController()

    async def get_source_record(self) -> Record:
        record = await self.db.select_one(
            "SELECT * FROM source_bucket WHERE id = ($1)", self.source_id
        )
        return record

    async def initialize_s3_client(self, encryption_key: str) -> str:
        # Create s3 client, add to class attribute and return source bucket name
        source: Record = await self.get_source_record()
        decrypted_access_key_id = self.encryption.decrypt_api_key(
            source["access_key_id"], encryption_key
        )
        decrypted_secret = self.encryption.decrypt_api_secret(
            source["secret_access_key"], encryption_key
        )
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=decrypted_access_key_id,
            aws_secret_access_key=decrypted_secret,
        )
        bucket_name: str = source["bucket_name"]
        return bucket_name

    async def s3_object_delete(self, encryption_key: str, key: str) -> dict:
        bucket_name: str = await self.initialize_s3_client(encryption_key)
        """
        delete_object always returns a 204 whether the object exists or not
        anything other than this should be regarded as a client error
        """
        if self.s3_client is None:
            raise HTTPException(status_code=500, detail="s3 client not initialized")

        response = self.s3_client.delete_object(Bucket=bucket_name, Key=key)
        try:
            meta = response["ResponseMetadata"]
            status = meta["HTTPStatusCode"]
            if status == 204:
                return {"result": "Deleted Successfully"}
            else:
                raise HTTPException(status_code=500, detail="S3 Client Error")
        except KeyError:
            raise HTTPException(status_code=500, detail="S3 Client Error")

    async def post_group(self, objects: list[dict]) -> list[dict]:
        output: list[dict] = []
        if self.db.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        async with self.db.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    query = """INSERT INTO item
                    (source_bucket_id, 
                    mime_type, 
                    file_path, 
                    file_size, 
                    created_by_id)
                    VALUES ($1, $2, $3, $4, $5) 
                    RETURNING *"""
                    for obj in objects:
                        values: tuple = (
                            self.source_id,
                            obj["mime_type"],
                            obj["key"],
                            obj["size"],
                            self.token_data.user_id,
                        )
                        result = await connection.fetchrow(query, values)
                        output.append(dict(result))
                    return output
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    async def import_from_source(self, encryption_key: str) -> list[dict]:
        # TODO: this method needs a way to filter out directories, extensions and mime types
        bucket_name: str = await self.initialize_s3_client(encryption_key)

        if self.s3_client is None:
            raise HTTPException(status_code=500, detail="s3 client not initialized")

        paginator = self.s3_client.get_paginator("list_objects_v2")
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
