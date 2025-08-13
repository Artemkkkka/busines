from fastapi import APIRouter

router = APIRouter()

@router.get("/ping", tags=["health"])
async def ping():
    return {"ping": "pong"}
