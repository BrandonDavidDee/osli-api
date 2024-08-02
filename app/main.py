from contextlib import asynccontextmanager

from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware

from app.authentication import routes as auth
from app.authentication.token import get_current_user
from app.db import db
from app.galleries import routes as galleries
from app.gallery_links import routes as gallery_links
from app.items import routes as items
from app.sources import routes as sources
from app.tags import routes as tags
from app.users import routes as users


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    await db.open_conn_pool()
    yield
    await db.close_pool()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:9000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def app_root():
    return {"OSLI": "(Multiple) Object Storage Library Index"}


app.include_router(
    auth.router,
    prefix="/api/authentication",
)

app.include_router(
    galleries.router,
    prefix="/api/galleries",
)

app.include_router(
    gallery_links.router,
    prefix="/api/gallery-links",
)

app.include_router(
    items.router,
    prefix="/api/items",
)

app.include_router(
    sources.router,
    prefix="/api/sources",
)

app.include_router(
    tags.router,
    prefix="/api/tags",
)

app.include_router(
    users.router,
    prefix="/api/users",
    dependencies=[Security(get_current_user)],
)
