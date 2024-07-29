import os

from fastapi import HTTPException
from asyncpg import Record

from app.authentication.models import AccessTokenData

from app.controller import BaseController
from app.sources.controller import SourceDetailController
from app.items.models import Item, SearchParams, ItemTag
from app.tags.models import Tag
from app.sources.models import SourceConfig


class ItemListController(SourceDetailController):
    def __init__(self, token_data: AccessTokenData, source_config_id: int):
        super().__init__(token_data, source_config_id)

    @staticmethod
    def get_filename(path):
        return os.path.basename(path)

    async def item_search(self, payload: SearchParams) -> dict:
        if len(payload.tag_ids):
            query = """SELECT
            count(*) OVER () AS total_count,
            i.*,
            sc.name,
            sc.bucket_name,
            sc.media_prefix,
            sc.grid_view
            FROM item AS i
            LEFT JOIN source_config AS sc ON sc.id = i.source_config_id
            LEFT JOIN tag_item as j ON j.item_id = i.id """
            placeholders = ", ".join(
                f"${i}" for i in range(7, 7 + len(payload.tag_ids))
            )
            query += f""" WHERE 
            (
              ($3 = '') OR (i.notes ILIKE '%' || $4 || '%') OR (i.file_path ILIKE '%' || $5 || '%')
            ) 
            AND j.tag_id IN ({placeholders})
            AND i.source_config_id = $6
            """
            # query += " GROUP BY i.id ORDER BY i.id DESC LIMIT $1 OFFSET $2"
            query += """ 
            GROUP BY i.id, sc.name, sc.bucket_name, sc.media_prefix, sc.grid_view
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            values: tuple = (
                payload.limit,
                payload.offset,
                payload.filter,
                payload.filter,
                payload.filter,
                self.source_config_id,
            )
            combined_values: tuple = values + tuple(payload.tag_ids)
            result: Record = await self.db.select_many(query, *combined_values)
        else:
            query = """SELECT
            count(*) OVER () AS total_count,
            i.*,
            sc.name,
            sc.bucket_name,
            sc.media_prefix,
            sc.grid_view
            FROM item AS i
            LEFT JOIN source_config AS sc ON sc.id = i.source_config_id
            WHERE (($3 = '') OR i.notes ILIKE '%' || $4 || '%' OR i.file_path ILIKE '%' || $5 || '%')
            AND i.source_config_id = $6
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            values: tuple = (
                payload.limit,
                payload.offset,
                payload.filter,
                payload.filter,
                payload.filter,
                self.source_config_id,
            )
            result: Record = await self.db.select_many(query, *values)

        output: list[Item] = []

        for row in result:
            item = Item(**row)
            item.source_config = SourceConfig(
                id=row["source_config_id"],
                name=row["name"],
                bucket_name=row["bucket_name"],
                media_prefix=row["media_prefix"],
                grid_view=row["grid_view"],
            )
            item.file_name = self.get_filename(row["file_path"])
            output.append(item)
        total_count = result[0]["total_count"] if result else 0

        if output:
            # we've joined the source config to each item:
            source_config = output[0].source_config
        else:
            # but if there are no results, we still want the list view page to have source info:
            source_config = await self.source_detail()

        return {
            "source_config": source_config,
            "total_count": total_count,
            "items": output,
        }


class ItemDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, item_id: int):
        super().__init__(token_data)
        self.item_id = item_id

    async def item_detail(self):
        query = """SELECT 
        i.*,
        sc.name,
        sc.bucket_name,
        sc.media_prefix,
        sc.grid_view,
        j.id as tag_item_id,
        tag.id as tag_id,
        tag.title as tag_title
        FROM item i 
        LEFT JOIN source_config AS sc ON sc.id = i.source_config_id
        LEFT JOIN tag_item as j ON j.item_id = i.id
        LEFT JOIN tag ON tag.id = j.tag_id
        WHERE i.id = $1
        """
        values: tuple = (self.item_id,)
        result: Record = await self.db.select_many(query, *values)

        if not result:
            raise HTTPException(status_code=404)

        base_row = result[0]

        item = Item(**base_row)
        item.source_config = SourceConfig(
            id=base_row["source_config_id"],
            name=base_row["name"],
            bucket_name=base_row["bucket_name"],
            media_prefix=base_row["media_prefix"],
            grid_view=base_row["grid_view"],
        )

        for record in result:
            if record['tag_item_id']:
                item_tag = ItemTag(
                    id=record['tag_item_id'],
                    tag=Tag(
                        id=record['tag_id'],
                        title=record['tag_title']
                    )
                )
                item.tags.append(item_tag)

        return item

    async def item_update(self, payload: Item):
        query = "UPDATE item SET notes = $1 WHERE id = $2 RETURNING *"
        values: tuple = (payload.notes, self.item_id,)
        await self.db.insert(query, *values)
        return payload
