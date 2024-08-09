from fastapi import APIRouter, Depends

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.me.controllers.links import MyLinksController
from app.me.controllers.saved_items import SavedItemsController

router = APIRouter()


@router.get("/saved")
async def saved(token_data: AccessTokenData = Depends(get_current_user)):
    return await SavedItemsController(token_data).get_saved_items()


@router.get("/links")
async def saved(token_data: AccessTokenData = Depends(get_current_user)):
    return await MyLinksController(token_data).get_links()
