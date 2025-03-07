import os
import re
from typing import Any

from asyncpg import Record, UniqueViolationError, create_pool
from fastapi import HTTPException, Response
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Database:
    def __init__(self) -> None:
        self.pool = None

    async def open_conn_pool(self) -> None:
        if self.pool is None:
            self.pool = await create_pool(
                min_size=1,
                max_size=10,
                command_timeout=60,
                user=os.getenv("DATABASE_USERNAME"),
                password=os.getenv("DATABASE_PASSWORD"),
                database=os.getenv("DATABASE_NAME"),
                host=os.getenv("DATABASE_HOST"),
                port=os.getenv("DATABASE_PORT"),
            )

    async def close_pool(self) -> None:
        if self.pool is not None:
            await self.pool.close()

    async def select_many(
        self, query: str, values: tuple[Any, ...] | Any | None = None
    ) -> list[Record]:
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    if values is None:
                        result: list[Record] = await connection.fetch(query)
                    elif isinstance(values, tuple):
                        result = await connection.fetch(query, *values)
                    else:
                        result = await connection.fetch(query, values)
                    return result
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    async def select_one(
        self, query: str, values: tuple[Any, ...] | Any
    ) -> Record | None:
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    if isinstance(values, tuple):
                        result: Record = await connection.fetchrow(query, *values)
                    else:
                        result = await connection.fetchrow(query, values)
                    if not result:
                        return None
                    return result
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    async def insert(self, query: str, values: tuple[Any, ...] | Any) -> dict:
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    if isinstance(values, tuple):
                        result = await connection.fetchrow(query, *values)
                    else:
                        result = await connection.fetchrow(query, values)
                    return dict(result)
                except UniqueViolationError:
                    raise HTTPException(
                        status_code=500, detail="Unique Violation Error!"
                    )
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    async def bulk_update(
        self, query_value_pairs: list[tuple[str, tuple[Any, ...] | Any]]
    ) -> None:
        """
        Execute multiple distinct SQL queries with corresponding values in a single transaction.

        :param query_value_pairs: List of tuples, each containing a query and its corresponding values.
        """
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")

        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    for query, values in query_value_pairs:
                        if isinstance(values, tuple):
                            await connection.execute(query, *values)
                        else:
                            await connection.execute(query, values)
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    async def delete_one(self, query: str, values: tuple[Any, ...] | Any) -> Response:
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        if not re.search(r"\bWHERE\b", query, re.IGNORECASE):
            raise HTTPException(
                status_code=500, detail="No WHERE clause in sql statement"
            )
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    if isinstance(values, tuple):
                        await connection.execute(query, *values)
                    else:
                        await connection.execute(query, values)
                    return Response()
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))


db = Database()
