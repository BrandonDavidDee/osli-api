import boto3
from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController, KeyEncryptionController


class S3ApiController(BaseController):
    def __init__(
        self, token_data: AccessTokenData, source_id: int, encryption_key: str
    ):
        super().__init__(token_data)
        self.source_id = source_id
        self.encryption_key = encryption_key
        self.s3_client = None
        self.encryption = KeyEncryptionController()

    async def get_source_record(self) -> Record:
        record = await self.db.select_one(
            "SELECT * FROM source_bucket WHERE id = ($1)", self.source_id
        )
        return record

    async def initialize_s3_client(self) -> str:
        # Create s3 client, add to class attribute and return source bucket name
        source: Record = await self.get_source_record()
        decrypted_access_key_id = self.encryption.decrypt_api_key(
            source["access_key_id"], self.encryption_key
        )
        decrypted_secret = self.encryption.decrypt_api_secret(
            source["secret_access_key"], self.encryption_key
        )
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=decrypted_access_key_id,
            aws_secret_access_key=decrypted_secret,
        )
        return source["bucket_name"]
