import re

from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.authentication.permissions import Permission
from app.authentication.scopes import find_permission, find_permission_group
from app.controller import BaseController
from app.users.models import UserDetail


class UserDetailController(BaseController):
    def __init__(self, token_data: AccessTokenData, user_id: int):
        super().__init__(token_data)
        self.user_id = user_id

    @staticmethod
    def parse_dynamic_scope(string: str) -> Permission | None:
        # replace_number_with_source_id
        match = re.search(r"\d+", string)
        if not match:
            return None
        source_id = match.group()
        if re.findall(r"\d+", string)[1:]:
            raise ValueError("More than one number found in the string")
        permission_name = re.sub(r"\d+", "{source_id}", string)
        permission = find_permission(permission_name)
        if not permission:
            return None
        permission.source_id = int(source_id)
        if not permission:
            return None
        return permission

    def get_user_permissions(self, user_scopes: list[str]) -> list[Permission]:
        """Dynamic scopes, regular permissions and permission groups
        are all together in user[scopes] and use string patterns and list groupings to
        determine which is which.
        """
        output = []
        for scope in user_scopes:
            found_group = find_permission_group(scope)
            has_source_id = self.parse_dynamic_scope(scope)
            found_permission = find_permission(scope)
            if found_group:
                for permission in found_group.permissions:
                    output.append(permission)
            elif has_source_id:
                # this is a scope set explicitly for a particular source_id
                output.append(has_source_id)
            elif found_permission:
                output.append(found_permission)

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
