from app.db import db


class GalleryLinkController:
    def __init__(self, link: str):
        self.db = db
        self.link = link

    async def get_gallery_link(self):
        query = "SELECT * FROM gallery_link WHERE link = $1"
        result = await self.db.select_one(query, self.link)
        return result
