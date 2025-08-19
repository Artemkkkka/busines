from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import workers
from app.models.team import Worker, TeamRole
from app.models.user import User


async def is_superuser(user: User) -> bool:
    return getattr(user, "is_superuser", False) is True


async def ensure_worker_exists(session: AsyncSession, user_id: int) -> Worker:
    worker = await workers.get_by_user_id(session, user_id)
    if worker is None:
        worker = Worker(user_id=user_id, team_id=None, role_in_team=TeamRole.employee)
        session.add(worker)
        await session.flush()
    return worker


async def is_team_admin(session: AsyncSession, user_id: int, team_id: int) -> bool:
    worker = await workers.get_by_user_and_team(session, user_id, team_id)
    if not worker:
        return False
    return worker.team_id == team_id and worker.role_in_team == TeamRole.admin


async def require_member(session: AsyncSession, user_id: int, team_id: int) -> Worker:
    w = await workers.get_by_user_and_team(session, user_id, team_id)
    if not w or w.team_id != team_id:
        raise HTTPException(status_code=403, detail="You are not a member of this team")
    return w


async def require_superuser_or_team_admin(
    session: AsyncSession, current_user: User, team_id: int
) -> None:
    if await is_superuser(current_user):
        return
    if await is_team_admin(session, current_user.id, team_id):
        return
    raise HTTPException(status_code=403, detail="Not enough permissions")


async def can_create_team(session: AsyncSession, user: User) -> bool:
    if await is_superuser(user):
        return True
    w = await workers.get_by_user_id(session, user.id)
    return bool(w and w.role_in_team == TeamRole.admin)  # глобальный admin (team_id может быть None)
