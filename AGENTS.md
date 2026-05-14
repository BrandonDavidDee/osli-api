# AGENTS.md — OSLI API

**OSLI** (Object Storage Library Index) is a FastAPI backend that indexes and manages media assets from two source types: **S3-compatible buckets** and **Vimeo accounts**. Everything is scoped to a *source* (a configured S3 bucket or Vimeo account stored in the DB).

---

## Architecture Overview

```
sources (bucket | vimeo)
  └─ items (item_bucket | item_vimeo)
       ├─ tags (tag_item_bucket | tag_item_vimeo)
       ├─ links (item_link — shared via /api/public/)
       └─ galleries (gallery → gallery_item → item_bucket | item_vimeo)
```

- `app/main.py` — routers registered with prefixes (`/api/authentication`, `/api/items`, `/api/sources`, etc.)
- `app/sources/` and `app/items/` each split into `bucket/` and `vimeo/` subdirectories with their own `routes.py`, `models.py`, and `controllers/`
- `app/public/` — **unauthenticated** share-link routes at `/api/public/gallery/{link}` and `/api/public/item/{link}`
- `app/schema.py` — SQLAlchemy ORM models used **only for Alembic migrations**, not for queries
- `app/db.py` — all queries use raw asyncpg SQL via the global `db` singleton (`Database` class)

## Database Layer

All DB access goes through `app/db.py`'s `Database` class methods: `select_many`, `select_one`, `insert`, `delete_one`, `bulk_update`. **Do not use SQLAlchemy sessions for queries.** SQLAlchemy (`app/schema.py`) is only used to autogenerate Alembic migration files.

asyncpg uses positional `$1, $2, ...` placeholders. Pass a tuple for multiple values, a single value for one.

## Controller Inheritance Chain

Every controller extends `BaseController` (`app/controller.py`), which provides `self.db`, `self.token_data`, `self.created_by_id`. Source-specific controllers extend further:

```
BaseController
  └─ S3ApiController (adds self.s3_client, self.encryption)
       └─ SourceBucketDetailController
            └─ ItemBucketListController / ItemBucketDetailController / ...
```

Vimeo follows the same pattern under `app/sources/vimeo/controllers/`.

## Authentication & Scopes

- JWT HS256 access tokens (30 min) + refresh tokens (5 days); token passed in `Authorization: Bearer <token>` header
- `"is_admin"` in scopes bypasses all permission checks
- Bucket/Vimeo permissions are **dynamic**: `bucket_{source_id}_item_read` — the `{source_id}` placeholder is resolved at runtime from the route's `source_id` query parameter
- Scope checking in routes uses `Security(get_current_user, scopes=["bucket_{source_id}_item_read"])`
- Permission groups (e.g. `group_bucket_item_manage`) are expanded to individual permissions at validation time — see `app/authentication/scopes.py`

## Credential Encryption

S3 `access_key_id`, `secret_access_key`, and Vimeo `access_token` are stored **encrypted** in the DB using Fernet symmetric encryption (`app/controller.py → KeyEncryptionController`). Routes that need to call S3/Vimeo accept an `encryption_key` query parameter (user-supplied passphrase) to decrypt credentials at request time. Required env vars: `API_KEY_SALT`, `API_SECRET_SALT`, `ACCESS_TOKEN_SALT`.

## `item_link` Table Design

A single `item_link` table with nullable `item_bucket_id` and `item_vimeo_id` FK columns (only one is set per row) keeps the public share URL scheme generic — `/share/ITEM/{uuid}` — rather than source-type-specific. See the docstring in `app/schema.py → ItemLink` for the rationale.

## Developer Workflows

```bash
# Run dev server
uvicorn app.main:app --reload

# Run tests (verbose + stdout)
pytest

# Type check
mypy app/

# Apply DB migrations
alembic upgrade head
# or
python do_alembic_upgrade.py

# Generate a new migration after schema changes
alembic revision --autogenerate -m "description"
```

Required `.env` vars: `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_NAME`, `DATABASE_HOST`, `DATABASE_PORT`, `SECRET_KEY`, `SITE_URL`, `API_KEY_SALT`, `API_SECRET_SALT`, `ACCESS_TOKEN_SALT`.

## Testing Conventions

- `tests/conftest.py` overrides `get_current_user` dependency globally: `app.dependency_overrides[get_current_user] = lambda: AccessTokenData(user_id="1")`
- DB methods are patched using `patch("app.db.Database.select_many")` — **not** `patch.object(db, ...)`, which fails for deeply nested controllers
- Fixtures: `dummy_user`, `dummy_source_bucket`, `dummy_source_vimeo`, `dummy_item_bucket`, `dummy_item_vimeo` are session-scoped; db mock fixtures (`mock_db_select_many`, `mock_db_select_one`, etc.) are function-scoped
- All tests use `FastAPI.TestClient` with the DB pool mocked out via `AsyncMock`

## Key Files

| File | Purpose |
|---|---|
| `app/controller.py` | `BaseController` + `KeyEncryptionController` — shared by all controllers |
| `app/db.py` | Global `db` singleton; all SQL runs through here |
| `app/schema.py` | SQLAlchemy models (Alembic only) |
| `app/authentication/permissions.py` | Scope/permission definitions and groups |
| `app/authentication/token.py` | JWT decode, scope resolution, `get_current_user` dependency |
| `tests/conftest.py` | Shared fixtures and auth override |
| `alembic/versions/` | Migration history; `ac7777f70b06_initial.py` has full schema |

