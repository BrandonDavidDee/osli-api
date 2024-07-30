from typing import Annotated

from fastapi import APIRouter, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.sources.vimeo.controller import SourcesVimeoController

router = APIRouter()


@router.get("")
async def source_list(
    token_data: Annotated[
        AccessTokenData, Security(get_current_user, scopes=["source_list"])
    ],
):
    return await SourcesVimeoController(token_data).get_list()
