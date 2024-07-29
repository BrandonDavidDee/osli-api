from typing import Annotated

from fastapi import APIRouter, Security, Depends

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.controller import ItemListController, ItemDetailController
from app.items.models import SearchParams, Item

router = APIRouter()


@router.post("")
async def item_search(
    source_config_id: int,
    payload: SearchParams,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    controller = ItemListController(token_data, source_config_id)
    return await controller.item_search(payload)


@router.get("/{item_id}")
async def item_detail(item_id: int, token_data: AccessTokenData = Depends(get_current_user)):
    return await ItemDetailController(token_data, item_id).item_detail()


@router.put("/{item_id}")
async def item_update(item_id: int, payload: Item, token_data: AccessTokenData = Depends(get_current_user)):
    return await ItemDetailController(token_data, item_id).item_update(payload)
