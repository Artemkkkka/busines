from fastapi import HTTPException

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Worker, TeamRole
from app.models.user import User


async def get_worker_or_404(session: AsyncSession, user_id: int) -> Worker:
    res = await session.execute(select(Worker).where(Worker.user_id == user_id))
    worker = res.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found for given user")
    return worker

async def ensure_worker_exists(session: AsyncSession, user_id: int) -> Worker:
    res = await session.execute(select(Worker).where(Worker.user_id == user_id))
    worker = res.scalar_one_or_none()
    if worker is None:
        worker = Worker(user_id=user_id, team_id=None, role_in_team=TeamRole.employee)
        session.add(worker)
        await session.flush()
    return worker

async def is_superuser(user: User) -> bool:
    return getattr(user, "is_superuser", False) is True

async def is_team_admin(session: AsyncSession, user_id: int, team_id: int) -> bool:
    res = await session.execute(select(Worker).where(Worker.user_id == user_id))
    worker = res.scalar_one_or_none()
    if not worker:
        return False
    return worker.team_id == team_id and worker.role_in_team == TeamRole.admin

async def require_superuser_or_team_admin(
    session: AsyncSession, current_user: User, team_id: int
) -> None:
    if await is_superuser(current_user):
        return
    if await is_team_admin(session, current_user.id, team_id):
        return
    raise HTTPException(status_code=403, detail="Not enough permissions")