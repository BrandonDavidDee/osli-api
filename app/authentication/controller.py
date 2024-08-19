from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.authentication.models import LoginBody, RefreshTokenData, TokenPair
from app.authentication.token import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
)
from app.db import db
from app.users.models import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthControllerBase:
    def __init__(self, request: Request):
        self.db = db
        self.request = request

    async def get_user_in_db(
        self, user_id: str | None, username: str | None
    ) -> UserInDB | None:
        if user_id:
            query = "SELECT * FROM auth_user WHERE id = ($1)"
            record = await self.db.select_one(query, int(user_id))
        elif username:
            query = "SELECT * FROM auth_user WHERE username = ($1)"
            record = await self.db.select_one(query, username)
        else:
            raise HTTPException(
                status_code=500, detail="Username or User id must be provided"
            )
        if not record:
            return None
        scopes: list[str] = record["scopes"].split(",") if record["scopes"] else []
        is_admin = record["is_admin"]
        if is_admin:
            scopes.append("is_admin")
        user = UserInDB(
            id=record["id"],
            is_active=record["is_active"],
            is_admin=is_admin,
            username=record["username"],
            hashed_password=record["hashed_password"],
            scopes=scopes,
        )

        return user

    async def create_token_pair(self, user: UserInDB) -> TokenPair:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_expires_on = datetime.now(timezone.utc) + access_token_expires
        access_token = self.create_token(
            data={"sub": str(user.id), "scopes": user.scopes},
            expires_on=access_expires_on,
        )
        refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_expires_on = datetime.now(timezone.utc) + refresh_token_expires
        refresh_token = self.create_token(
            data={"sub": str(user.id)},
            expires_on=refresh_expires_on,
        )
        return TokenPair(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @staticmethod
    def create_token(data: dict, expires_on: datetime) -> str:
        to_encode: dict = data.copy()
        to_encode.update({"exp": expires_on})
        encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


class LoginController(AuthControllerBase):
    async def login(self, body: LoginBody) -> TokenPair:
        user: UserInDB | None = await self.authenticate_user(
            user_id=None, username=body.username, password=body.password
        )
        if not user:
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Inactive User")
        return await self.create_token_pair(user)

    async def authenticate_user(
        self, user_id: str | None, username: str | None, password: str
    ) -> UserInDB | None:
        user: UserInDB | None = await self.get_user_in_db(
            user_id=user_id, username=username
        )
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        result: bool = pwd_context.verify(plain_password, hashed_password)
        return result


class RefreshController(AuthControllerBase):
    async def refresh_tokens(self) -> TokenPair:
        token: str = self.get_token_from_header()
        token_sub: RefreshTokenData = await self.validate_refresh_token(token)
        user: UserInDB | None = await self.get_user_in_db(
            user_id=token_sub.user_id, username=None
        )
        if not user:
            raise HTTPException(status_code=500, detail="User In Sub Not Found")

        if not user.is_active:
            raise HTTPException(status_code=401, detail="Inactive User")
        return await self.create_token_pair(user)

    def get_token_from_header(self) -> str:
        headers = self.request.headers
        authorization = headers.get("authorization")
        try:
            token: str = authorization.partition(" ")[2]
        except (AttributeError, IndexError):
            raise HTTPException(
                status_code=401, detail="Error getting token from Header"
            )
        return token

    @staticmethod
    async def validate_refresh_token(token: str) -> RefreshTokenData:
        try:
            payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return RefreshTokenData(user_id=payload["sub"])
        except (JWTError, ValidationError, KeyError):
            raise HTTPException(
                status_code=401, detail="Error validating refresh token"
            )
