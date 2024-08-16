from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_user_list() -> str:
    return "user list root"
