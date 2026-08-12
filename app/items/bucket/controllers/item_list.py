import re

from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.items.bucket.models import ItemBucket
from app.items.models import SearchParams
from app.sources.bucket.controllers.bucket_detail import SourceBucketDetailController
from app.sources.bucket.models import SourceBucket
from app.sources.models import SourceType


class ItemBucketListController(SourceBucketDetailController):
    # Matches either a double-quoted phrase (captured without quotes) or a
    # single whitespace-delimited token. Used to split a filter string like
    # `Apple "Red Car" Black dog` into ["Apple", "Red Car", "Black", "dog"].
    _TOKEN_PATTERN = re.compile(r'"([^"]+)"|(\S+)')

    def __init__(self, token_data: AccessTokenData, source_id: int):
        super().__init__(token_data, source_id)

    def _tokenize_filter(self, filter_str: str) -> list[str]:
        terms: list[str] = []
        for quoted, unquoted in self._TOKEN_PATTERN.findall(filter_str):
            term = quoted.strip() if quoted else unquoted.strip()
            if term:
                terms.append(term)
        return terms

    def _build_search_condition(
        self,
        payload: SearchParams,
        column_names: list[str],
        start_index: int,
    ) -> tuple[str, list[str]]:
        terms = self._tokenize_filter(payload.filter.strip())
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
            source.bucket_name,
            source.media_prefix,
            source.grid_view
        FROM item_bucket AS i
        LEFT JOIN source_bucket AS source ON source.id = i.source_bucket_id
        LEFT JOIN tag_item_bucket AS j ON j.item_bucket_id = i.id
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
            ["i.notes", "i.file_path", "i.title", "t.title"],
            start_index=4,
        )
        base_query += f"\n        {self._search_filter_sql(search_condition)}"
        values.extend(filter_values)

        if payload.tag_ids:
            placeholders = ", ".join(
                f"${i}"
                for i in range(len(values) + 1, len(values) + 1 + len(payload.tag_ids))
            )
            term_joiner = " OR " if payload.filter_mode == "or" else " AND "
            base_query += f" {term_joiner} j.tag_id IN ({placeholders})"
            values.extend(payload.tag_ids)

        # Dynamically set the placeholder for source_bucket_id
        source_bucket_placeholder = f"${len(values) + 1}"
        base_query += f" AND i.source_bucket_id = {source_bucket_placeholder}"

        values.append(self.source_id)

        # Finalizing query
        base_query += """ 
        GROUP BY i.id, source.title, source.bucket_name, source.media_prefix, source.grid_view
        ORDER BY i.id DESC LIMIT $1 OFFSET $2"""

        result: Record = await self.db.select_many(base_query, tuple(values))
        output: list[ItemBucket] = []

        for row in result:
            item = ItemBucket(**row)
            if row["source_bucket_id"]:
                item.source = SourceBucket(
                    id=row["source_bucket_id"],
                    title=row["source_title"],
                    bucket_name=row["bucket_name"],
                    media_prefix=row["media_prefix"],
                    grid_view=row["grid_view"],
                    source_type=SourceType.BUCKET,
                )
            item.file_name = self.get_filename(row["file_path"])
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
