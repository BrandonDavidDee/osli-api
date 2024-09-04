from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.items.models import SearchParams
from app.items.vimeo.models import ItemVimeo
from app.sources.models import SourceType
from app.sources.vimeo.controllers.vimeo_detail import SourceVimeoDetailController
from app.sources.vimeo.models import SourceVimeo


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
            result: Record = await self.db.select_many(query, combined_values)
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
            values = (
                payload.limit,
                payload.offset,
                payload.filter,
                payload.filter,
                payload.filter,
                payload.filter,
                self.source_id,
            )
            result = await self.db.select_many(query, values)

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
