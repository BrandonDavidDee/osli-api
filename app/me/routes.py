from typing import Annotated

from fastapi import APIRouter, Depends, Security

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.me.controllers.my_links import MyLinksController
from app.me.controllers.saved_items import SavedItemsController
from app.me.models import SavedItem

router = APIRouter()


@router.get("")
def test_perms(
    source_id: int,
    token_data: Annotated[
        AccessTokenData,
        Security(
            get_current_user,
            scopes=["bucket_{source_id}_item_delete"],
        ),
    ],
) -> AccessTokenData:
    return token_data


@router.get("/saved-items")
async def saved_items(
    token_data: AccessTokenData = Depends(get_current_user),
) -> list[SavedItem]:
    return await SavedItemsController(token_data).get_saved_items()


@router.get("/links")
async def saved(token_data: AccessTokenData = Depends(get_current_user)) -> dict:
    return await MyLinksController(token_data).get_links()
