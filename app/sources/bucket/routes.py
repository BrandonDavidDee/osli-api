from typing import Annotated

from fastapi import APIRouter, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.sources.bucket.controllers.bucket_detail import SourceBucketDetailController
from app.sources.bucket.controllers.bucket_list import SourceBucketListController
from app.sources.bucket.controllers.s3_api import S3ApiController

router = APIRouter()


@router.get("")
async def source_list(
    token_data: Annotated[
        AccessTokenData, Security(get_current_user, scopes=["source_list"])
    ],
):
    return await SourceBucketListController(token_data).get_list()


@router.get("/{source_id}")
async def source_detail(
    source_id: int,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    controller = SourceBucketDetailController(token_data, source_id)
    return await controller.source_detail()


@router.get("/{source_id}/import")
async def source_import(
    encryption_key: str,
    source_id: int,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    # TODO: this function needs a way to filter out directories, extensions and mime types
    return await S3ApiController(
        token_data,
        source_id,
        encryption_key,
    ).import_from_source()
