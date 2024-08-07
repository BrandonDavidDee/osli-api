from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, Security, UploadFile

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.bucket.controller import (
    BatchUploadController,
    ItemBucketDetailController,
    ItemBucketListController,
)
from app.items.bucket.models import ItemBucket
from app.items.models import ItemTag, SearchParams

router = APIRouter()


@router.post("")
async def item_batch_upload(
    source_id: int,
    encryption_key: str,
    files: list[UploadFile] = File(...),
    token_data: AccessTokenData = Depends(get_current_user),
):
    controller = BatchUploadController(token_data, source_id, encryption_key)
    return await controller.s3_batch_upload(files=files)


@router.post("/search")
async def item_search(
    source_id: int,
    payload: SearchParams,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    controller = ItemBucketListController(token_data, source_id)
    return await controller.item_search(payload)


@router.get("/{item_id}")
async def item_detail(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    return await ItemBucketDetailController(token_data, item_id).item_detail()


@router.put("/{item_id}")
async def item_update(
    item_id: int,
    payload: ItemBucket,
    token_data: AccessTokenData = Depends(get_current_user),
):
    return await ItemBucketDetailController(token_data, item_id).item_update(payload)


@router.post("/{item_id}/tags")
async def item_tag_create(
    item_id: int,
    payload: ItemTag,
    token_data: AccessTokenData = Depends(get_current_user),
) -> ItemTag:
    controller = ItemBucketDetailController(token_data, item_id)
    return await controller.item_tag_create(payload)


@router.delete("/{item_id}/tags/{tag_item_bucket_id}")
async def item_tag_delete(
    item_id: int,
    tag_item_bucket_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
) -> Response:
    controller = ItemBucketDetailController(token_data, item_id)
    return await controller.item_tag_delete(tag_item_bucket_id)
