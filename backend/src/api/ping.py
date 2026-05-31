from fastapi import APIRouter
from src.schemas.ping import PingResponse

router = APIRouter(prefix='/ping')


@router.get('/')
async def ping():
    return PingResponse()
