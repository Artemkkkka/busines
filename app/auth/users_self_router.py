import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from .db import User
from .schemas import UserRead, UserSelfUpdate
from .manager import get_user_manager
from .auth import current_user as current_active_user


router = APIRouter(prefix="/users", tags=["users"])


def build_self_router():
    @router.get("/me", response_model=UserRead)
    async def get_me(user: User = Depends(current_active_user)):
        return user

    @router.delete("/me", status_code=204)
    async def delete_me(
        user: User = Depends(current_active_user),
        user_manager = Depends(get_user_manager),
    ):
        await user_manager.delete(user)
        return

    @router.patch("/me", response_model=UserRead)
    async def patch_me_email(
        payload: UserSelfUpdate,
        request: Request,
        user: User = Depends(current_active_user),
        user_manager = Depends(get_user_manager),
    ):
        user.email = payload.email
        updated = await user_manager.user_db.update(user)
        await user_manager.on_after_update(updated, request)
        return updated

    return router
