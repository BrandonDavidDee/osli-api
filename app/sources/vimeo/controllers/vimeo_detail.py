from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.sources.models import SourceType
from app.sources.vimeo.controllers.vimeo_api import VimeoApiController
from app.sources.vimeo.models import SourceVimeo


class SourceVimeoDetailController(VimeoApiController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)
        self.source_id = source_id

    async def source_create(self):
        pass

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

    async def source_update(self, passphrase: str, payload: SourceVimeo) -> int:
        query = """UPDATE source_vimeo SET
        title = $1,
        client_identifier = $2,
        client_secret = $3,
        access_token = $4,
        grid_view = $5
        WHERE id = $6 RETURNING *"""
        encrypted_client_id = self.encryption.encrypt_api_key(
            payload.client_identifier, passphrase
        )
        encrypted_client_secret = self.encryption.encrypt_api_secret(
            payload.client_secret, passphrase
        )
        encrypted_access_token = self.encryption.encrypt_access_token(
            payload.access_token, passphrase
        )
        values: tuple = (
            payload.title,
            encrypted_client_id,
            encrypted_client_secret,
            encrypted_access_token,
            payload.grid_view,
            self.source_id,
        )
        result: Record = await self.db.insert(query, values)
        return result["id"]
