from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.team import TeamRole
from app.crud import workers as crud_workers
from app.utils.team_utils import is_superuser


async def grant_global_admin(session: AsyncSession, *, actor: User, target_user_id: int) -> None:
    if not await is_superuser(actor):
        raise HTTPException(status_code=403, detail="Superuser only")
    w = await crud_workers.ensure_exists(session, target_user_id)
    w.role_in_team = TeamRole.admin     # глобальный админ (team_id может быть None)
    # commit — здесь, т.к. это отдельная операция
    await session.commit()
