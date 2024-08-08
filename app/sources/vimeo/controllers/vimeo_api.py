import base64

import httpx
from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController, KeyEncryptionController


class VimeoApiController(BaseController):
    def __init__(
        self, token_data: AccessTokenData, source_id: int, encryption_key: str
    ):
        super().__init__(token_data)
        self.source_id = source_id
        self.encryption_key = encryption_key
        self.encryption = KeyEncryptionController()

    async def get_source_record(self) -> Record:
        record = await self.db.select_one(
            "SELECT * FROM source_vimeo WHERE id = ($1)", self.source_id
        )
        return record

    async def get_vimeo_access_token(self):
        source: Record = await self.get_source_record()
        encrypted_access_token = source["access_token"]
        return self.encryption.decrypt_access_token(
            encrypted_access_token, self.encryption_key
        )

    async def get_thumbnails(self, video_id: str | int) -> str:
        url = f"https://api.vimeo.com/videos/{video_id}"
        access_token = await self.get_vimeo_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as session:
            response = await session.get(url, headers=headers)
            if response.status_code == 200:
                video = response.json()
                thumbnails = video.get("pictures", {}).get("sizes", [])
                large = thumbnails[4]
                link = large["link"]
                # link_with_play_button = large["link_with_play_button"]
                return link
            else:
                raise HTTPException(
                    status_code=403,
                    detail=f"Failed to get thumbs: {response.status_code} - {response.text}",
                )

    @staticmethod
    async def generate_vimeo_access_token():
        # Leaving this here for future in case I decide to enable token rotation.
        client_id = ""  # will be hashed value in db
        client_secret = ""  # will be hashed value in db
        scopes = "public private"
        url = "https://api.vimeo.com/oauth/authorize/client"

        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }

        payload = {"grant_type": "client_credentials", "scope": scopes}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                access_token = response.json()["access_token"]
                print(f"Access Token: {access_token}")
                return access_token
            else:
                print(
                    f"Failed to generate access token: {response.status_code} - {response.text}"
                )
                return None
