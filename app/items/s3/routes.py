from typing import Annotated

from fastapi import APIRouter, Depends, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.items.s3.controller import ItemS3DetailController, ItemS3ListController
from app.items.models import SearchParams
from app.items.s3.models import ItemS3

router = APIRouter()


@router.post("")
async def item_search(
    source_s3_id: int,
    payload: SearchParams,
    token_data: Annotated[AccessTokenData, Security(get_current_user, scopes=["view"])],
):
    controller = ItemS3ListController(token_data, source_s3_id)
    return await controller.item_search(payload)


@router.get("/{item_id}")
async def item_detail(
    item_id: int, token_data: AccessTokenData = Depends(get_current_user)
):
    return await ItemS3DetailController(token_data, item_id).item_detail()


@router.put("/{item_id}")
async def item_update(
    item_id: int, payload: ItemS3, token_data: AccessTokenData = Depends(get_current_user)
):
    return await ItemS3DetailController(token_data, item_id).item_update(payload)
