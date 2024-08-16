import os
from contextlib import asynccontextmanager

from asyncpg import Record, UniqueViolationError, create_pool
from fastapi import HTTPException, Response
from sqlalchemy.ext.declarative import declarative_base

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

    async def select_many(self, query: str, *values) -> list[Record]:
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    result: list[Record] = await connection.fetch(query, *values)
                    # return [dict(row) for row in result]
                    return result
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    async def select_one(self, query: str, *values) -> Record | None:
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    result: Record = await connection.fetchrow(query, *values)
                    if not result:
                        return None
                    return result
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    async def insert(self, query: str, *values) -> dict:
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    result = await connection.fetchrow(query, *values)
                    return dict(result)
                except UniqueViolationError:
                    # raising this here with this message only works if slugs are the only cols with a unique constr
                    raise HTTPException(
                        status_code=500, detail="That slug is already reserved"
                    )
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    async def delete_one(self, query: str, *values) -> Response:
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute(query, *values)
                    return Response()
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))

    @asynccontextmanager
    async def get_connection(self, unique_err_message: str | None = None):
        if self.pool is None:
            raise HTTPException(status_code=500, detail="Database pool is empty")
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    yield connection
                except UniqueViolationError as exc:
                    raise HTTPException(
                        status_code=400,
                        detail=unique_err_message or f"Unique Violation Error: {exc}",
                    )
                except Exception as exc:
                    raise HTTPException(status_code=500, detail=str(exc))


db = Database()
