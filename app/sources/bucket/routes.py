from fastapi import APIRouter, Depends

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.sources.bucket.controllers.bucket_detail import SourceBucketDetailController
from app.sources.bucket.controllers.bucket_list import SourceBucketListController
from app.sources.bucket.models import SourceBucket

router = APIRouter()


@router.get("")
async def source_list(
    token_data: AccessTokenData = Depends(get_current_user),
) -> list[SourceBucket]:
    return await SourceBucketListController(token_data).get_list()


@router.get("/{source_id}")
async def source_detail(
    source_id: int, token_data: AccessTokenData = Depends(get_current_user)
) -> SourceBucket:
    controller = SourceBucketDetailController(token_data, source_id)
    return await controller.source_detail()


@router.put("/{source_id}")
async def source_update(
    source_id: int,
    passphrase: str,
    payload: SourceBucket,
    token_data: AccessTokenData = Depends(get_current_user),
) -> int:
    controller = SourceBucketDetailController(token_data, source_id)
    return await controller.source_update(passphrase, payload)
