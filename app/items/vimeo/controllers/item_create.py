from app.authentication.models import AccessTokenData
from app.items.vimeo.models import ItemVimeo
from app.sources.vimeo.controllers.vimeo_api import VimeoApiController


class ItemVimeoCreateController(VimeoApiController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)

    async def item_create(self, encryption_key: str, payload: ItemVimeo):
        thumbnail = await self.get_thumbnails(encryption_key, payload.video_id)
        query = """INSERT INTO item_vimeo
        (source_vimeo_id, video_id, title, thumbnail, notes, created_by_id)
        values ($1, $2, $3, $4, $5, $6) RETURNING *"""
        values: tuple = (
            self.source_id,
            payload.video_id,
            payload.title,
            thumbnail,
            payload.notes,
            int(self.token_data.user_id),
        )
        return await self.db.insert(query, *values)
