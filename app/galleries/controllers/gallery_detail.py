import os

from asyncpg import Connection, Record
from fastapi import HTTPException, Response

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.galleries.models import Gallery, GalleryItem
from app.items.bucket.models import ItemBucket
from app.items.vimeo.models import ItemVimeo
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType
from app.users.models import User


class GalleryAssemblyStub:
    @staticmethod
    def get_filename(path: str | None) -> str | None:
        if path is None:
            return None
        return str(os.path.basename(path))

    def assemble_gallery(
        self,
        result: list[Record],
        use_link_title: bool = False,
    ) -> Gallery:
        base_row: Record = result[0]
        title = base_row["public_link_title"] if use_link_title else base_row["title"]
        items: list[GalleryItem] = []

        seen_items = {}

        gallery = Gallery(
            id=base_row["id"],
            title=title,
            description=base_row["description"],
            date_created=base_row["date_created"],
            created_by=User(
                id=base_row["user_id"],
                username=base_row["username"],
                is_active=base_row["user_is_active"],
            ),
        )
        for row in result:
            gallery_item_id = row["gallery_item_id"]
            if gallery_item_id and gallery_item_id not in seen_items:
                gallery_item = GalleryItem(
                    id=row["gallery_item_id"],
                    item_order=row["item_order"],
                    date_created=row["item_date_created"],
                )
                if row["item_bucket_id"]:
                    item_bucket = ItemBucket(
                        id=row["item_bucket_id"],
                        mime_type=row["bucket_mime_type"],
                        file_path=row["bucket_file_path"],
                        file_size=row["bucket_file_size"],
                        date_created=row["bucket_date_created"],
                    )
                    item_bucket.file_name = self.get_filename(row["bucket_file_path"])
                    if row["source_bucket_id"]:
                        item_bucket.source = SourceBucket(
                            id=row["source_bucket_id"],
                            title=row["source_bucket_title"],
                            media_prefix=row["source_bucket_media_prefix"],
                            source_type=SourceType.BUCKET,
                        )
                    gallery_item.source_id = row["source_bucket_id"]
                    gallery_item.source_type = SourceType.BUCKET
                    gallery_item.item_bucket = item_bucket
                if row["item_vimeo_id"]:
                    item_vimeo = ItemVimeo(
                        id=row["item_vimeo_id"],
                        title=row["item_vimeo_title"],
                        thumbnail=row["item_vimeo_thumbnail"],
                        video_id=row["item_vimeo_video_id"],
                        height=row["item_vimeo_height"],
                        width=row["item_vimeo_width"],
                        date_created=row["item_vimeo_date_created"],
                    )
                    gallery_item.source_id = row["source_vimeo_id"]
                    gallery_item.source_type = SourceType.VIMEO
                    gallery_item.item_vimeo = item_vimeo
                    seen_items[gallery_item_id] = gallery_item
                items.append(gallery_item)

        items.sort(key=lambda x: x.item_order)
        gallery.items = items
        return gallery


class GalleryDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, gallery_id: int):
        super().__init__(token_data)
        self.gallery_id = gallery_id
        self.assembly_stub = GalleryAssemblyStub()

    @staticmethod
    async def update_item_order(
        connection: Connection, items: list[GalleryItem]
    ) -> None:
        for item in items:
            query = "UPDATE gallery_item SET item_order = $1 WHERE id = $2"
            values: tuple = (
                item.item_order,
                item.id,
            )
            await connection.fetchrow(query, values)

    async def gallery_update(self, gallery_id: int, payload: Gallery) -> Gallery:
        async with self.db.get_connection() as connection:
            try:
                query = "UPDATE gallery SET title = $1, description = $2 WHERE id = $3"
                values: tuple = (
                    payload.title,
                    payload.description,
                    gallery_id,
                )
                await connection.fetchrow(query, values)
                await self.update_item_order(connection, payload.items)
                return payload
            except HTTPException as exc:
                raise exc
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc))

    async def get_gallery_detail(self) -> Gallery:
        query = """SELECT 
        g.*,
        
        u.id as user_id,
        u.username,
        u.is_active as user_is_active,
        
        gi.id as gallery_item_id,
        gi.item_order,
        gi.date_created as item_date_created,

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
        iv.source_vimeo_id,
        iv.width as item_vimeo_width,
        iv.height as item_vimeo_height,
        iv.title as item_vimeo_title,
        iv.thumbnail as item_vimeo_thumbnail,
        iv.video_id as item_vimeo_video_id,
        iv.date_created as item_vimeo_date_created,
        iv.created_by_id as item_vimeo_created_by_id

        FROM gallery AS g 
        LEFT JOIN auth_user AS u ON u.id = g.created_by_id
        
        LEFT JOIN gallery_item AS gi ON gi.gallery_id = g.id
        LEFT JOIN item_bucket AS ib ON ib.id = gi.item_bucket_id
        LEFT JOIN source_bucket AS sb ON sb.id = ib.source_bucket_id
        LEFT JOIN item_vimeo AS iv ON iv.id = gi.item_vimeo_id

        WHERE g.id = $1"""
        result: list[Record] = await self.db.select_many(query, self.gallery_id)
        if not result:
            raise HTTPException(status_code=404)
        return self.assembly_stub.assemble_gallery(result=result)

    async def gallery_item_create(self, payload: GalleryItem) -> GalleryItem:
        query = """INSERT INTO gallery_item
        (gallery_id, 
        item_bucket_id, 
        item_vimeo_id, 
        item_order, 
        created_by_id)
        VALUES ($1, $2, $3, $4, $5) 
        RETURNING *"""
        created_by_id = self.created_by_id
        if payload.source_type == SourceType.BUCKET and payload.item_bucket is not None:
            values: tuple = (
                self.gallery_id,
                payload.item_bucket.id,
                None,
                payload.item_order,
                created_by_id,
            )
        elif payload.source_type == SourceType.VIMEO and payload.item_vimeo is not None:
            values = (
                self.gallery_id,
                None,
                payload.item_vimeo.id,
                payload.item_order,
                created_by_id,
            )
        else:
            raise HTTPException(status_code=500, detail="Unknown Source Type")
        result: Record = await self.db.insert(query, values)
        inserted_item_id: int = result["id"]
        payload.id = inserted_item_id
        return payload

    async def gallery_item_delete(self, gallery_item_id: int) -> Response:
        query = "DELETE FROM gallery_item WHERE id = $1"
        return await self.db.delete_one(query, gallery_item_id)
