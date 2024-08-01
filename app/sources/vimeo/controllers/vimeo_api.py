import httpx
import base64
from app.authentication.models import AccessTokenData
from app.controller import BaseController


class VimeoApiController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    @staticmethod
    async def generate_vimeo_access_token():
        # Leaving this here for future in case I decide to enable token rotation.
        client_id = ''  # will be hashed value in db
        client_secret = ''  # will be hashed value in db
        scopes = 'public private'
        url = 'https://api.vimeo.com/oauth/authorize/client'

        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
        }

        payload = {
            'grant_type': 'client_credentials',
            'scope': scopes
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                access_token = response.json()['access_token']
                print(f"Access Token: {access_token}")
                return access_token
            else:
                print(f"Failed to generate access token: {response.status_code} - {response.text}")
                return None

    @staticmethod
    def get_vimeo_access_token():
        # will be hashed value in db
        return ''

    async def get_thumbnails(self, video_id: str | int):
        url = f'https://api.vimeo.com/videos/{video_id}'

        access_token = self.get_vimeo_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient() as session:
            response = await session.get(url, headers=headers)
            if response.status_code == 200:
                video = response.json()
                thumbnails = video.get('pictures', {}).get('sizes', [])
                large = thumbnails[4]
                link = large['link']
                link_with_play_button = large['link_with_play_button']
                print(link)
                print(link_with_play_button)
            else:
                print(f"Failed to get thumbs: {response.status_code} - {response.text}")
                return None
