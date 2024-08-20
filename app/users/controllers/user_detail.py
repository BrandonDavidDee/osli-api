import re

from asyncpg import Record
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.authentication.permissions import Permission
from app.authentication.scopes import find_permission, find_permission_group
from app.controller import BaseController
from app.users.models import User


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

    def get_user_permissions(self, user_scopes: list[str]) -> dict:
        """Dynamic scopes, regular permissions and permission groups
        are all together in user[scopes] and use string patterns and list groupings to
        determine which is which.
        """
        permissions = []
        permission_groups = []
        for scope in user_scopes:
            found_group = find_permission_group(scope)
            has_source_id = self.parse_dynamic_scope(scope)
            found_permission = find_permission(scope)
            if found_group:
                permission_groups.append(found_group)
            elif has_source_id:
                # this is a scope set explicitly for a particular source_id
                permissions.append(has_source_id)
            elif found_permission:
                permissions.append(found_permission)
        return {"permissions": permissions, "permission_groups": permission_groups}

    async def get_user_detail(self) -> User:
        row: Record = await self.db.select_one(
            "SELECT * FROM auth_user WHERE id = $1", self.user_id
        )
        if not row:
            raise HTTPException(status_code=404)
        user = User(
            id=row["id"],
            is_active=row["is_active"],
            is_admin=row["is_admin"],
            username=row["username"],
            notes=row["notes"],
            date_created=row["date_created"],
        )
        user.scopes = row["scopes"].split(",") if row["scopes"] else []
        permissions: dict = self.get_user_permissions(user.scopes)
        user.permissions = permissions["permissions"]
        user.permission_groups = permissions["permission_groups"]
        return user

    async def update_user_scopes(self, payload: User) -> User:
        if not payload.scopes:
            scope_value: str | None = None
        else:
            scope_value = ",".join(payload.scopes)
        query = "UPDATE auth_user SET scopes = $1 WHERE id = $2 RETURNING scopes"
        values: tuple = (
            scope_value,
            self.user_id,
        )
        result: Record = await self.db.insert(query, values)
        if result["scopes"]:
            updated_scopes = result["scopes"].split(",")
            permissions: dict = self.get_user_permissions(updated_scopes)
            payload.permissions = permissions["permissions"]
            payload.permission_groups = permissions["permission_groups"]
        else:
            payload.permissions = []
            payload.permission_groups = []
        return payload
