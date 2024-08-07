from asyncpg import Record
from fastapi import HTTPException, Response

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.items.models import ItemTag, SearchParams
from app.items.vimeo.models import ItemVimeo
from app.sources.models import SourceType
from app.sources.vimeo.controller import SourceVimeoDetailController
from app.sources.vimeo.models import SourceVimeo
from app.tags.models import Tag


class ItemVimeoListController(SourceVimeoDetailController):
    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)

    async def item_search(self, payload: SearchParams) -> dict:
        if len(payload.tag_ids):
            query = """SELECT
            count(*) OVER () AS total_count,
            i.*,
            source.title as source_title,
            source.client_identifier,
            source.client_secret,
            source.access_token,
            source.grid_view
            FROM item_vimeo AS i
            LEFT JOIN source_vimeo AS source ON source.id = i.source_vimeo_id
            LEFT JOIN tag_item_vimeo as j ON j.item_vimeo_id = i.id """
            placeholders = ", ".join(
                f"${i}" for i in range(8, 8 + len(payload.tag_ids))
            )
            query += f""" WHERE 
            (
              ($3 = '') 
              OR (i.notes ILIKE '%' || $4 || '%') 
              OR (i.video_id ILIKE '%' || $5 || '%')
              OR (i.title ILIKE '%' || $6 || '%')
            ) 
            AND j.tag_id IN ({placeholders})
            AND i.source_vimeo_id = $7
            """
            query += """ 
            GROUP BY 
            i.id, source.title, source.client_identifier, 
            source.client_secret, source.access_token, source.grid_view
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            values: tuple = (
                payload.limit,
                payload.offset,
                payload.filter,
                payload.filter,
                payload.filter,
                payload.filter,
                self.source_id,
            )
            combined_values: tuple = values + tuple(payload.tag_ids)
            result: Record = await self.db.select_many(query, *combined_values)
        else:
            query = """SELECT
            count(*) OVER () AS total_count,
            i.*,
            source.title as source_title,
            source.client_identifier,
            source.client_secret,
            source.access_token,
            source.grid_view
            FROM item_vimeo AS i
            LEFT JOIN source_vimeo AS source ON source.id = i.source_vimeo_id
            WHERE (
            ($3 = '') 
            OR (i.notes ILIKE '%' || $4 || '%') 
            OR (i.video_id ILIKE '%' || $5 || '%')
            OR (i.title ILIKE '%' || $6 || '%')
            )
            AND i.source_vimeo_id = $7
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            values: tuple = (
                payload.limit,
                payload.offset,
                payload.filter,
                payload.filter,
                payload.filter,
                payload.filter,
                self.source_id,
            )
            result: Record = await self.db.select_many(query, *values)

        output: list[ItemVimeo] = []

        for row in result:
            item = ItemVimeo(**row)
            if row["source_vimeo_id"]:
                item.source = SourceVimeo(
                    id=row["source_vimeo_id"],
                    title=row["source_title"],
                    client_identifier=row["client_identifier"],
                    client_secret=row["client_secret"],
                    access_token=row["access_token"],
                    grid_view=row["grid_view"],
                    source_type=SourceType.VIMEO,
                )
            # item.file_name = self.get_filename(row["file_path"])
            output.append(item)
        total_count = result[0]["total_count"] if result else 0

        if output:
            # we've joined the source to each item:
            source = output[0].source
        else:
            # but if there are no results, we still want the list view page to have source info:
            source = await self.source_detail()

        return {
            "source": source,
            "total_count": total_count,
            "items": output,
        }


class ItemVimeoDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data)
        self.item_id = item_id

    async def item_detail(self):
        query = """SELECT 
        i.*,
        source.title as source_title,
        source.client_identifier,
        source.client_secret,
        source.access_token,
        source.grid_view,
        j.id as tag_item_id,
        tag.id as tag_id,
        tag.title as tag_title
        FROM item_vimeo i 
        LEFT JOIN source_vimeo AS source ON source.id = i.source_vimeo_id
        LEFT JOIN tag_item_vimeo as j ON j.item_vimeo_id = i.id
        LEFT JOIN tag ON tag.id = j.tag_id
        WHERE i.id = $1
        """
        values: tuple = (self.item_id,)
        result: Record = await self.db.select_many(query, *values)

        if not result:
            raise HTTPException(status_code=404)

        base_row = result[0]

        item = ItemVimeo(**base_row)
        item.source = SourceVimeo(
            id=base_row["source_vimeo_id"],
            title=base_row["source_title"],
            client_identifier=base_row["client_identifier"],
            client_secret=base_row["client_secret"],
            access_token=base_row["access_token"],
            grid_view=base_row["grid_view"],
            source_type=SourceType.BUCKET,
        )

        for record in result:
            if record["tag_item_id"]:
                item_tag = ItemTag(
                    id=record["tag_item_id"],
                    tag=Tag(id=record["tag_id"], title=record["tag_title"]),
                )
                item.tags.append(item_tag)

        return item

    async def item_update(self, payload: ItemVimeo):
        query = "UPDATE item_vimeo SET title = $1, notes = $2 WHERE id = $3 RETURNING *"
        values: tuple = (
            payload.title,
            payload.notes,
            self.item_id,
        )
        await self.db.insert(query, *values)
        return payload

    async def item_tag_create(self, payload: ItemTag) -> ItemTag:
        query = "INSERT INTO tag_item_vimeo (tag_id, item_vimeo_id) VALUES ($1, $2) RETURNING id"
        values: tuple = (
            payload.tag.id,
            self.item_id,
        )
        result: Record = await self.db.insert(query, *values)
        payload.id = result["id"]
        return payload

    async def item_tag_delete(self, tag_item_vimeo_id: int) -> Response:
        query = "DELETE FROM tag_item_vimeo WHERE id = $1"
        return await self.db.delete_one(query, tag_item_vimeo_id)
