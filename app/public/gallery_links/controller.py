from fastapi import HTTPException

from app.db import db
from app.galleries.controllers.gallery_detail import GalleryAssemblyStub


class GalleryLinkController:
    def __init__(self, link: str):
        self.db = db
        self.link = link
        self.assembly_stub = GalleryAssemblyStub()

    async def get_gallery_link(self):
        query = """SELECT 
        gl.title as public_link_title,
        gl.is_active,

        g.*,
        
        u.id as user_id,
        u.username,
        u.is_active as user_is_active,

        gi.id as gallery_item_id,
        gi.item_order,

        ib.id as item_bucket_id,
        ib.title as bucket_title,
        ib.mime_type as bucket_mime_type,
        ib.file_path as bucket_file_path,
        ib.file_size as bucket_file_size,
        ib.date_created as bucket_date_created,
        ib.created_by_id as bucket_created_by_id,

        sb.id as source_bucket_id,
        sb.title as source_bucket_title,
        sb.media_prefix as source_bucket_media_prefix,

        iv.id as item_vimeo_id,
        iv.title as item_vimeo_title,
        iv.thumbnail as item_vimeo_thumbnail,
        iv.video_id as item_vimeo_video_id,
        iv.date_created as item_vimeo_date_created,
        iv.created_by_id as item_vimeo_created_by_id
        FROM gallery_link AS gl 
        LEFT JOIN gallery AS g ON g.id = gl.gallery_id
        LEFT JOIN auth_user AS u ON u.id = g.created_by_id
        LEFT JOIN gallery_item AS gi ON gi.gallery_id = g.id
        LEFT JOIN item_bucket AS ib ON ib.id = gi.item_bucket_id
        LEFT JOIN source_bucket AS sb ON sb.id = ib.source_bucket_id
        LEFT JOIN item_vimeo AS iv ON iv.id = gi.item_vimeo_id
        WHERE gl.link = $1
        """
        result = await self.db.select_many(query, self.link)
        if not result:
            raise HTTPException(status_code=404, detail="Link not found")
        is_active = bool(result[0]["is_active"])
        if not is_active:
            raise HTTPException(status_code=404, detail="Link not active")
        use_link_title = bool(result[0]["public_link_title"])
        return self.assembly_stub.assemble_gallery(result, use_link_title)
