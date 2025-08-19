from fastapi import APIRouter, HTTPException, status

from app.models.team import TeamRole
from app.utils.team_utils import ensure_worker_exists, is_superuser
from app.core.dependencies import SessionDep, CurrentUser

sys_router = APIRouter(prefix="/system", tags=["system"])


@sys_router.post("/workers/{user_id}:admin", status_code=status.HTTP_204_NO_CONTENT)
async def grant_admin_worker(user_id: int, session: SessionDep, me: CurrentUser):
    if not await is_superuser(me):
        raise HTTPException(status_code=403, detail="Superuser only")
    w = await ensure_worker_exists(session, user_id)
    w.role_in_team = TeamRole.admin
    await session.commit()
    return None
