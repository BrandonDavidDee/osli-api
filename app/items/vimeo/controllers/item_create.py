from app.authentication.models import AccessTokenData
from app.items.vimeo.models import ItemVimeo
from app.sources.vimeo.controllers.vimeo_api import VimeoApiController


class ItemVimeoCreateController(VimeoApiController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)

    async def item_create(self, encryption_key: str, payload: ItemVimeo) -> int:
        video_data = await self.get_thumbnails(encryption_key, payload.video_id)
        query = """INSERT INTO item_vimeo
        (source_vimeo_id, 
        video_id, 
        title, 
        thumbnail,
        width,
        height, 
        notes, 
        created_by_id)
        values ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id"""
        values: tuple = (
            self.source_id,
            payload.video_id,
            payload.title,
            video_data["thumbnail"],
            video_data["width"],
            video_data["height"],
            payload.notes,
            self.created_by_id,
        )
        result = await self.db.insert(query, values)
        inserted_id: int = result["id"]
        return inserted_id
