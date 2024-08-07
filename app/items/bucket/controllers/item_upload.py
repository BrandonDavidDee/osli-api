import mimetypes

from asyncpg import Record
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile

from app.authentication.models import AccessTokenData
from app.items.bucket.models import ItemBucket
from app.sources.bucket.controllers.s3_api import S3ApiController

TEMP_KEY_PREFIX = "dev-images"


class BatchUploadController(S3ApiController):
    def __init__(
        self, token_data: AccessTokenData, source_id: int, encryption_key: str
    ):
        super().__init__(token_data, source_id, encryption_key)

    async def s3_batch_upload(self, files: list[UploadFile]):
        bucket_name: str = await self.initialize_s3_client()
        output = []
        for (file,) in zip(files):
            contents = await file.read()
            file_size = len(contents)
            safe_filename = self.make_safe_filename(file.filename)
            key = f"{TEMP_KEY_PREFIX}/{safe_filename}"

            # TODO: mimetype guess duplicated in base controller
            content_type, _ = mimetypes.guess_type(file.filename)
            if not content_type:
                content_type = "application/octet-stream"

            query = """INSERT INTO item_bucket
            (source_bucket_id, mime_type, file_path, file_size, date_created, created_by_id)
            values ($1, $2, $3, $4, $5, $6) RETURNING *"""
            values: tuple = (
                self.source_id,
                content_type,
                key,
                file_size,
                self.now,
                int(self.token_data.user_id),
            )
            output.append(key)

            try:
                self.s3_client.put_object(
                    Body=contents,
                    Bucket=bucket_name,
                    Key=key,
                    ContentType=file.content_type,
                )
                result: Record = await self.db.insert(query, *values)
                output.append(ItemBucket(**result))
            except ClientError as e:
                raise HTTPException(status_code=500, detail="S3 Client Error")
        return {"new_keys": output}
