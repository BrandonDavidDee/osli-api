from typing import Annotated

from fastapi import APIRouter, Depends, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.sources.vimeo.controllers.vimeo_detail import SourceVimeoDetailController
from app.sources.vimeo.controllers.vimeo_list import SourcesVimeoListController
from app.sources.vimeo.models import SourceVimeo

router = APIRouter()


@router.get("")
async def source_list(token_data: AccessTokenData = Depends(get_current_user)):
    return await SourcesVimeoListController(token_data).get_list()


@router.get("/{source_id}")
async def source_detail(
    source_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    return await SourceVimeoDetailController(token_data, source_id).source_detail()


@router.put("/{source_id}")
async def source_update(
    source_id: int,
    passphrase: str,
    payload: SourceVimeo,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    return await SourceVimeoDetailController(token_data, source_id).source_update(
        passphrase, payload
    )
