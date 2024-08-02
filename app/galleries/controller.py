import os

from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.galleries.models import Gallery, GalleryItem
from app.items.bucket.models import ItemBucket
from app.items.vimeo.models import ItemVimeo


class GalleryListController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_galleries(self):
        query = "SELECT * FROM gallery"
        return await self.db.select_many(query)


class GalleryAssemblyStub:
    @staticmethod
    def get_filename(path):
        return os.path.basename(path)

    def assemble_gallery(self, result: list[Record], use_link_title: bool = False):
        base_row: Record = result[0]
        title = base_row["link_title"] if use_link_title else base_row["title"]
        gallery = Gallery(
            id=base_row["id"],
            title=title,
            description=base_row["description"],
            date_created=base_row["date_created"],
        )
        for row in result:
            if row["gallery_item_id"]:
                gallery_item = GalleryItem(
                    id=row["gallery_item_id"], item_order=row["item_order"]
                )
                if row["item_bucket_id"]:
                    item_bucket = ItemBucket(
                        id=row["item_bucket_id"],
                        mime_type=row["bucket_mime_type"],
                        file_path=row["bucket_file_path"],
                        file_size=row["bucket_file_size"],
                        date_created=row["bucket_date_created"],
                        created_by_id=row["bucket_created_by_id"],
                    )
                    item_bucket.file_name = self.get_filename(row["bucket_file_path"])
                    gallery_item.item_bucket = item_bucket
                if row["item_vimeo_id"]:
                    item_vimeo = ItemVimeo(
                        id=row["item_vimeo_id"],
                        title=row["item_vimeo_title"],
                        thumbnail=row["item_vimeo_thumbnail"],
                        video_id=row["item_vimeo_video_id"],
                        date_created=row["item_vimeo_date_created"],
                        created_by_id=row["item_vimeo_created_by_id"],
                    )
                    gallery_item.item_vimeo = item_vimeo
                gallery.items.append(gallery_item)
        return gallery


class GalleryDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, gallery_id: int):
        super().__init__(token_data)
        self.gallery_id = gallery_id
        self.assembly_stub = GalleryAssemblyStub()

    async def get_gallery_detail(self):
        query = """SELECT 
        g.*,
        gi.id as gallery_item_id,
        gi.item_order,
        
        ib.id as item_bucket_id,
        ib.title as bucket_title,
        ib.mime_type as bucket_mime_type,
        ib.file_path as bucket_file_path,
        ib.file_size as bucket_file_size,
        ib.date_created as bucket_date_created,
        ib.created_by_id as bucket_created_by_id,
        
        iv.id as item_vimeo_id,
        iv.title as item_vimeo_title,
        iv.thumbnail as item_vimeo_thumbnail,
        iv.video_id as item_vimeo_video_id,
        iv.date_created as item_vimeo_date_created,
        iv.created_by_id as item_vimeo_created_by_id
    
        FROM gallery AS g 
        LEFT JOIN gallery_item AS gi ON gi.gallery_id = g.id
        LEFT JOIN item_bucket AS ib ON ib.id = gi.item_bucket_id
        LEFT JOIN item_vimeo AS iv ON iv.id = gi.item_vimeo_id
        WHERE g.id = $1 ORDER BY gi.item_order
        """
        result = await self.db.select_many(query, self.gallery_id)
        if not result:
            raise HTTPException(status_code=404)
        return self.assembly_stub.assemble_gallery(result)
