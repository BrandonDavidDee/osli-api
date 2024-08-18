from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.users.models import UserDetail


class UserDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, user_id: int):
        super().__init__(token_data)
        self.user_id = user_id

    async def get_user_detail(self) -> UserDetail:
        row: Record = await self.db.select_one(
            "SELECT * FROM auth_user WHERE id = $1", self.user_id
        )
        if not row:
            raise HTTPException(status_code=404)
        user = UserDetail(
            id=row["id"],
            is_active=row["is_active"],
            is_admin=row["is_admin"],
            username=row["username"],
            notes=row["notes"],
            date_created=row["date_created"],
        )
        return user
