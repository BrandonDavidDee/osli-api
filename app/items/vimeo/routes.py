from typing import Annotated

from fastapi import APIRouter, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.vimeo.controller import ItemVimeoListController
from app.items.models import SearchParams

router = APIRouter()


@router.post("")
async def item_vimeo_list(
    source_id: int,
    payload: SearchParams,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    controller = ItemVimeoListController(token_data, source_id)
    return await controller.item_search(payload)

