from typing import Annotated

from fastapi import APIRouter, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.sources.controller import (
    SourceDetailController,
    SourceImportController,
    SourcesController,
)

router = APIRouter()


@router.get("")
async def source_list(
    token_data: Annotated[
        AccessTokenData, Security(get_current_user, scopes=["source_list"])
    ],
):
    return await SourcesController(token_data).get_list()


@router.get("/{source_config_id}")
async def source_detail(
    source_config_id: int,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    controller = SourceDetailController(token_data, source_config_id)
    return await controller.source_detail()


@router.get("/{source_config_id}/import")
async def source_import(
        source_config_id: int,
        token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])]
):
    # TODO: this function needs a way to filter out directories
    return await SourceImportController(token_data, source_config_id).import_from_source()
