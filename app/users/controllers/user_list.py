from asyncpg import Record

from app.authentication.models import AccessTokenData
from app.controller import BaseController
from app.users.models import User


class UserListController(BaseController):
    def __init__(self, token_data: AccessTokenData):
        super().__init__(token_data)

    async def get_list(self) -> list[User]:
        result: list[Record] = await self.db.select_many("SELECT * FROM auth_user")
        output = []
        for row in result:
            user = User(
                id=row["id"],
                is_active=row["is_active"],
                is_admin=row["is_admin"],
                username=row["username"],
                notes=row["notes"],
                date_created=row["date_created"],
            )
            output.append(user)
        return output
