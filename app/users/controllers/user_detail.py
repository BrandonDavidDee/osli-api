from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.authentication.scopes import Permission, all_permissions
from app.controller import BaseController
from app.users.models import UserDetail


class UserDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, user_id: int):
        super().__init__(token_data)
        self.user_id = user_id

    @staticmethod
    def find_permission(scope: str):
        result: Permission | None = next(
            (perm for perm in all_permissions if perm.name == scope), None
        )
        return result

    def get_user_permissions(self, user_scopes: list[str]):
        output = []
        # needs to handle dynamic scopes and permission groups too
        for scope in user_scopes:
            found = self.find_permission(scope)
            if found:
                output.append(found)
        return output

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
        user.scopes = row["scopes"].split(",") if row["scopes"] else []
        user.permissions = self.get_user_permissions(user.scopes)
        return user
