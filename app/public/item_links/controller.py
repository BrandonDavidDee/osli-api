import os

from asyncpg import Record
from fastapi import HTTPException

from app.db import db
from app.items.bucket.models import ItemBucket
from app.items.vimeo.models import ItemVimeo
from app.public.item_links.models import PublicItemLink
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType


class PublicItemLinkController:
    def __init__(self, link: str):
        self.db = db
        self.link = link

    @staticmethod
    def get_filename(path) -> str:
        return os.path.basename(path)

    async def get_item_link(self):
        query = """SELECT 
        il.title as public_link_title,
        il.is_active,
        il.expiration_date,
        
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
        
        FROM item_link il 
        LEFT JOIN item_bucket AS ib ON ib.id = il.item_bucket_id
        LEFT JOIN source_bucket AS sb ON sb.id = ib.source_bucket_id
        LEFT JOIN item_vimeo AS iv ON iv.id = il.item_vimeo_id
        WHERE il.link = $1
        """
        result: list[Record] = await self.db.select_many(query, self.link)
        if not result:
            raise HTTPException(status_code=404, detail="Link not found")
        base_row: Record = result[0]

        is_active = bool(base_row["is_active"])
        if not is_active:
            raise HTTPException(status_code=404, detail="Link not active")

        use_link_title = bool(base_row["public_link_title"])
        title: str | None = None

        if use_link_title:
            title = base_row["public_link_title"]

        item_link = PublicItemLink(
            title=title,
            expiration_date=base_row["expiration_date"],
        )
        for row in result:
            if row["item_bucket_id"]:
                if not use_link_title:
                    item_link.title = row["bucket_title"]

                item_bucket = ItemBucket(
                    id=row["item_bucket_id"],
                    mime_type=row["bucket_mime_type"],
                    file_path=row["bucket_file_path"],
                    file_size=row["bucket_file_size"],
                    date_created=row["bucket_date_created"],
                    created_by_id=row["bucket_created_by_id"],
                )
                item_bucket.file_name = self.get_filename(row["bucket_file_path"])
                if row["source_bucket_id"]:
                    item_bucket.source = SourceBucket(
                        id=row["source_bucket_id"],
                        title=row["source_bucket_title"],
                        media_prefix=row["source_bucket_media_prefix"],
                        source_type=SourceType.BUCKET,
                    )
                item_link.source_type = SourceType.BUCKET
                item_link.item_bucket = item_bucket
            if row["item_vimeo_id"]:
                if not use_link_title:
                    item_link.title = row["item_vimeo_title"]

                item_vimeo = ItemVimeo(
                    id=row["item_vimeo_id"],
                    title=row["item_vimeo_title"],
                    thumbnail=row["item_vimeo_thumbnail"],
                    video_id=row["item_vimeo_video_id"],
                    date_created=row["item_vimeo_date_created"],
                    created_by_id=row["item_vimeo_created_by_id"],
                )
                item_link.source_type = SourceType.VIMEO
                item_link.item_vimeo = item_vimeo

        return item_link
