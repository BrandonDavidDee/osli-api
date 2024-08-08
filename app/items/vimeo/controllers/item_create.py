from app.authentication.models import AccessTokenData
from app.items.vimeo.models import ItemVimeo
from app.sources.vimeo.controllers.vimeo_api import VimeoApiController


class ItemVimeoCreateController(VimeoApiController):
    def __init__(
        self, token_data: AccessTokenData, source_id: int, encryption_key: str
    ):
        super().__init__(token_data, source_id, encryption_key)

    async def item_create(self, payload: ItemVimeo):
        thumbnail = await self.get_thumbnails(payload.video_id)
        query = """INSERT INTO item_vimeo
        (source_vimeo_id, video_id, title, thumbnail, notes, date_created, created_by_id)
        values ($1, $2, $3, $4, $5, $6, $7) RETURNING *"""
        values: tuple = (
            self.source_id,
            payload.video_id,
            payload.title,
            thumbnail,
            payload.notes,
            self.now,
            int(self.token_data.user_id),
        )
        return await self.db.insert(query, *values)
