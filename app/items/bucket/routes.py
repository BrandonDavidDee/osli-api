from fastapi import APIRouter, Depends, File, Response, Security, UploadFile

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.bucket.controllers.item_delete import ItemBucketDeleteController
from app.items.bucket.controllers.item_detail import ItemBucketDetailController
from app.items.bucket.controllers.item_links import ItemBucketLinkController
from app.items.bucket.controllers.item_list import ItemBucketListController
from app.items.bucket.controllers.item_save import ItemBucketSaveController
from app.items.bucket.controllers.item_tags import ItemBucketTagController
from app.items.bucket.controllers.item_upload import BatchUploadController
from app.items.bucket.models import ItemBucket
from app.items.models import ItemLink, ItemTag, SearchParams

router = APIRouter()


@router.post("")
async def item_batch_upload(
    source_id: int,
    encryption_key: str,
    files: list[UploadFile] = File(...),
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["bucket_{source_id}_item_create"]
    ),
) -> dict:
    controller = BatchUploadController(token_data, source_id)
    return await controller.s3_batch_upload(encryption_key=encryption_key, files=files)


@router.post("/search")
async def item_search(
    source_id: int,
    payload: SearchParams,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["bucket_{source_id}_item_read"]
    ),
) -> dict:
    controller = ItemBucketListController(token_data, source_id)
    return await controller.item_search_new(payload)


@router.get("/{item_id}")
async def item_detail(
    source_id: int,
    item_id: int,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["bucket_{source_id}_item_read"]
    ),
) -> ItemBucket:
    return await ItemBucketDetailController(
        token_data, source_id, item_id
    ).item_detail()


@router.put("/{item_id}")
async def item_update(
    source_id: int,
    item_id: int,
    payload: ItemBucket,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["bucket_{source_id}_item_update"]
    ),
) -> ItemBucket:
    return await ItemBucketDetailController(token_data, source_id, item_id).item_update(
        payload
    )


@router.put("/{item_id}/delete")
async def item_delete(
    item_id: int,
    source_id: int,
    encryption_key: str,
    payload: ItemBucket,
    token_data: AccessTokenData = Depends(get_current_user),
) -> int:
    controller = ItemBucketDeleteController(token_data=token_data, source_id=source_id)
    return await controller.delete_item(
        encryption_key=encryption_key, item_id=item_id, payload=payload
    )


@router.get("/{item_id}/related")
async def get_related(
    source_id: int,
    item_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
) -> dict:
    return await ItemBucketDetailController(
        token_data, source_id, item_id
    ).get_related()


@router.post("/{item_id}/tags")
async def item_tag_create(
    source_id: int,
    item_id: int,
    payload: ItemTag,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["bucket_{source_id}_item_update"]
    ),
) -> ItemTag:
    controller = ItemBucketTagController(token_data, item_id)
    return await controller.item_tag_create(payload)


@router.delete("/{item_id}/tags/{tag_item_bucket_id}")
async def item_tag_delete(
    source_id: int,
    item_id: int,
    tag_item_bucket_id: int,
    token_data: AccessTokenData = Security(
        get_current_user, scopes=["bucket_{source_id}_item_update"]
    ),
) -> Response:
    controller = ItemBucketTagController(token_data, item_id)
    return await controller.item_tag_delete(tag_item_bucket_id)


@router.post("/{item_id}/links")
async def item_link_create(
    item_id: int,
    payload: ItemLink,
    token_data: AccessTokenData = Depends(get_current_user),
) -> ItemLink:
    controller = ItemBucketLinkController(token_data, item_id)
    return await controller.item_link_create(payload)


@router.get("/{item_id}/links")
async def item_links(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
) -> ItemBucket:
    controller = ItemBucketLinkController(token_data, item_id)
    return await controller.get_item_links()


@router.put("/{item_id}/links/{item_link_id}")
async def item_link_update(
    item_id: int,
    item_link_id: int,
    payload: ItemLink,
    token_data: AccessTokenData = Depends(get_current_user),
) -> ItemLink:
    controller = ItemBucketLinkController(token_data, item_id)
    return await controller.item_link_update(item_link_id, payload)


@router.delete("/{item_id}/links/{item_link_id}")
async def item_link_delete(
    item_id: int,
    item_link_id: int,
    token_data: AccessTokenData = Depends(get_current_user),
) -> int:
    controller = ItemBucketLinkController(token_data, item_id)
    return await controller.item_link_delete(item_link_id)


@router.post("/{item_id}/save")
async def save_item(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
) -> None:
    return await ItemBucketSaveController(token_data, item_id).save_item()


@router.delete("/{item_id}/save")
async def delete_saved_item(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
) -> None:
    return await ItemBucketSaveController(token_data, item_id).delete_saved_item()
