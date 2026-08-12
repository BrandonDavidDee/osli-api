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

    def _build_search_condition(
        self,
        payload: SearchParams,
        column_names: list[str],
        start_index: int,
    ) -> tuple[str, list[str]]:
        terms = [term for term in payload.filter.strip().split() if term]
        if not terms:
            return "", []

        term_joiner = " OR " if payload.filter_mode == "or" else " AND "
        term_clauses: list[str] = []
        values: list[str] = []
        placeholder_index = start_index

        for term in terms:
            column_clauses = []
            for column_name in column_names:
                values.append(term)
                column_clauses.append(
                    f"({column_name} ILIKE '%' || ${placeholder_index} || '%')"
                )
                placeholder_index += 1
            term_clauses.append("(" + " OR ".join(column_clauses) + ")")

        return "(" + term_joiner.join(term_clauses) + ")", values

    def _search_filter_sql(self, search_condition: str) -> str:
        if search_condition:
            return f"AND (($3 = '') OR {search_condition})"
        return "AND ($3 = '')"

    async def item_search_new(self, payload: SearchParams) -> dict:
        base_query = """SELECT
            count(*) OVER () AS total_count,
            i.*,
            source.title as source_title,
            source.client_identifier,
            source.client_secret,
            source.access_token,
            source.grid_view
        FROM item_vimeo AS i
        LEFT JOIN source_vimeo AS source ON source.id = i.source_vimeo_id
        LEFT JOIN tag_item_vimeo AS j ON j.item_vimeo_id = i.id
        LEFT JOIN tag AS t ON t.id = j.tag_id
        WHERE 1=1
        """

        values: list = [
            payload.limit,
            payload.offset,
            payload.filter,
        ]

        search_condition, filter_values = self._build_search_condition(
            payload,
            ["i.notes", "i.video_id", "i.title", "t.title"],
            start_index=4,
        )
        base_query += f"\n        {self._search_filter_sql(search_condition)}"
        values.extend(filter_values)

        if payload.tag_ids:
            placeholders = ", ".join(
                f"${i}"
                for i in range(len(values) + 1, len(values) + 1 + len(payload.tag_ids))
            )
            base_query += f" AND j.tag_id IN ({placeholders})"
            values.extend(payload.tag_ids)

        source_vimeo_placeholder = f"${len(values) + 1}"
        base_query += f" AND i.source_vimeo_id = {source_vimeo_placeholder}"

        values.append(self.source_id)

        # Finalizing query
        base_query += """ 
        GROUP BY i.id, source.title, source.client_identifier, source.client_secret, source.access_token, source.grid_view
        ORDER BY i.id DESC LIMIT $1 OFFSET $2"""

        result: Record = await self.db.select_many(base_query, tuple(values))
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

    async def item_search_old(self, payload: SearchParams) -> dict:
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
            LEFT JOIN tag_item_vimeo as j ON j.item_vimeo_id = i.id
            WHERE 1=1"""
            search_condition, filter_values = self._build_search_condition(
                payload,
                ["i.notes", "i.video_id", "i.title"],
                start_index=4,
            )
            query += f"\n            {self._search_filter_sql(search_condition)}"
            values: tuple = (
                payload.limit,
                payload.offset,
                payload.filter,
            )
            combined_values = values + tuple(filter_values)
            placeholders = ", ".join(
                f"${i}"
                for i in range(
                    len(combined_values) + 1,
                    len(combined_values) + 1 + len(payload.tag_ids),
                )
            )
            combined_values += tuple(payload.tag_ids)
            source_id_placeholder = len(combined_values) + 1
            query += f"""
            AND j.tag_id IN ({placeholders})
            AND i.source_vimeo_id = ${source_id_placeholder}
            """
            query += """ 
            GROUP BY 
            i.id, source.title, source.client_identifier, 
            source.client_secret, source.access_token, source.grid_view
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            combined_values = combined_values + (self.source_id,)
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
            WHERE 1=1"""
            search_condition, filter_values = self._build_search_condition(
                payload,
                ["i.notes", "i.video_id", "i.title"],
                start_index=4,
            )
            query += f"\n            {self._search_filter_sql(search_condition)}"
            source_id_placeholder = 4 + len(filter_values) + 1
            query += f"""
            AND i.source_vimeo_id = ${source_id_placeholder}
            ORDER BY i.id DESC LIMIT $1 OFFSET $2"""
            values = (
                payload.limit,
                payload.offset,
                payload.filter,
            )
            result = await self.db.select_many(
                query, values + tuple(filter_values) + (self.source_id,)
            )

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
