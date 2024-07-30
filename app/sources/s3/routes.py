from typing import Annotated

from fastapi import APIRouter, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.sources.s3.controller import (
    SourceS3DetailController,
    SourceS3ImportController,
    SourcesS3Controller,
)

router = APIRouter()


@router.get("")
async def source_list(
    token_data: Annotated[
        AccessTokenData, Security(get_current_user, scopes=["source_list"])
    ],
):
    return await SourcesS3Controller(token_data).get_list()


@router.get("/{source_s3_id}")
async def source_detail(
    source_s3_id: int,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    controller = SourceS3DetailController(token_data, source_s3_id)
    return await controller.source_detail()


@router.get("/{source_id}/import")
async def source_import(
    source_id: int,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    # TODO: this function needs a way to filter out directories, extensions and mime types
    return await SourceS3ImportController(token_data, source_id).import_from_source()
