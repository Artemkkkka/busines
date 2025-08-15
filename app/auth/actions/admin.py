from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.auth.actions.create_superuser import create_superuser


router = APIRouter(prefix="/admin", tags=["admin"])


class SuperuserIn(BaseModel):
    email: EmailStr
    password: str


@router.post("/superusers", status_code=status.HTTP_201_CREATED, summary="Create superuser")
async def create_superuser_endpoint(body: SuperuserIn):
    try:
        user = await create_superuser(email=body.email, password=body.password)
        return user
    except Exception as exc:
        msg = str(exc)
        if "already exists" in msg.lower() or "unique" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Не удалось создать суперпользователя: {msg}")
