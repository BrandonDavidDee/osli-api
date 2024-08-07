import os

from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.galleries.models import Gallery, GalleryItem, GalleryLink
from app.items.bucket.models import ItemBucket
from app.items.vimeo.models import ItemVimeo
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType
from app.users.models import User


class GalleryAssemblyStub:
    @staticmethod
    def get_filename(path) -> str:
        return os.path.basename(path)

    def assemble_gallery(
        self,
        result: list[Record],
        use_link_title: bool = False,
        include_links: bool = False,
    ) -> Gallery:
        base_row: Record = result[0]
        title = base_row["public_link_title"] if use_link_title else base_row["title"]
        items: list[GalleryItem] = []
        links: list[GalleryLink] = []

        seen_items = {}
        seen_links = {}

        gallery = Gallery(
            id=base_row["id"],
            title=title,
            description=base_row["description"],
            date_created=base_row["date_created"],
        )
        for row in result:
            gallery_item_id = row["gallery_item_id"]
            if gallery_item_id and gallery_item_id not in seen_items:
                gallery_item = GalleryItem(
                    id=row["gallery_item_id"],
                    item_order=row["item_order"],
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
                    if row["source_bucket_id"]:
                        item_bucket.source = SourceBucket(
                            id=row["source_bucket_id"],
                            title=row["source_bucket_title"],
                            media_prefix=row["source_bucket_media_prefix"],
                            source_type=SourceType.BUCKET,
                        )
                    gallery_item.source_type = SourceType.BUCKET
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
                    gallery_item.source_type = SourceType.VIMEO
                    gallery_item.item_vimeo = item_vimeo
                    seen_items[gallery_item_id] = gallery_item
                items.append(gallery_item)

            if include_links:
                link_id = row["link_id"]
                if link_id and link_id not in seen_links:
                    view_count = row["link_view_count"] if row["link_view_count"] else 0
                    gallery_link = GalleryLink(
                        id=row["link_id"],
                        title=row["link_title"],
                        link=row["link_link"],
                        expiration_date=row["link_expiration_date"],
                        view_count=view_count,
                        date_created=row["link_date_created"],
                        created_by=User(
                            id=row["user_id"],
                            username=row["username"],
                            is_active=row["user_is_active"],
                        ),
                    )
                    links.append(gallery_link)
                    seen_links[link_id] = gallery_link

        items.sort(key=lambda x: x.item_order)
        gallery.items = items

        if include_links:
            links.sort(key=lambda x: x.date_created, reverse=True)
            gallery.links = links

        return gallery


class GalleryDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, gallery_id: int):
        super().__init__(token_data)
        self.gallery_id = gallery_id
        self.assembly_stub = GalleryAssemblyStub()

    async def get_gallery_detail(self) -> Gallery:
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

        sb.id as source_bucket_id,
        sb.title as source_bucket_title,
        sb.media_prefix as source_bucket_media_prefix,

        iv.id as item_vimeo_id,
        iv.title as item_vimeo_title,
        iv.thumbnail as item_vimeo_thumbnail,
        iv.video_id as item_vimeo_video_id,
        iv.date_created as item_vimeo_date_created,
        iv.created_by_id as item_vimeo_created_by_id,

        gl.id as link_id,
        gl.title as link_title,
        gl.link as link_link,
        gl.expiration_date as link_expiration_date,
        gl.view_count as link_view_count,
        gl.date_created as link_date_created,

        u.id as user_id,
        u.username,
        u.is_active as user_is_active

        FROM gallery AS g 
        LEFT JOIN gallery_item AS gi ON gi.gallery_id = g.id
        LEFT JOIN item_bucket AS ib ON ib.id = gi.item_bucket_id
        LEFT JOIN source_bucket AS sb ON sb.id = ib.source_bucket_id
        LEFT JOIN item_vimeo AS iv ON iv.id = gi.item_vimeo_id

        LEFT JOIN gallery_link AS gl ON gl.gallery_id = g.id
        LEFT JOIN auth_user AS u ON u.id = gl.created_by_id

        WHERE g.id = $1"""
        result: list[Record] = await self.db.select_many(query, self.gallery_id)
        if not result:
            raise HTTPException(status_code=404)
        return self.assembly_stub.assemble_gallery(result=result, include_links=True)
