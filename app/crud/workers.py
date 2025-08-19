from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Worker
from app.models.team import TeamRole


async def get_by_user_id(session: AsyncSession, user_id: int) -> Worker | None:
    res = await session.execute(select(Worker).where(Worker.user_id == user_id))
    return res.scalar_one_or_none()


async def get_by_user_and_team(session: AsyncSession, user_id: int, team_id: int) -> Worker | None:
    res = await session.execute(
        select(Worker).where(Worker.user_id == user_id, Worker.team_id == team_id)
    )
    return res.scalar_one_or_none()


async def get_by_user_id_or_404(session: AsyncSession, user_id: int) -> Worker:
    worker = await get_by_user_id(session, user_id)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found for given user")
    return worker


async def create_membership(session: AsyncSession, *, user_id: int, team_id: int, role: TeamRole) -> Worker:
    w = Worker(user_id=user_id, team_id=team_id, role_in_team=role)
    session.add(w)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Membership already exists")
    return w


async def ensure_exists(session: AsyncSession, user_id: int) -> Worker:
    worker = await get_by_user_id(session, user_id)
    if worker is None:
        worker = Worker(user_id=user_id, team_id=None, role_in_team=TeamRole.employee)
        session.add(worker)
        await session.flush()
    return worker


async def list_by_team(session: AsyncSession, team_id: int) -> list[Worker]:
    res = await session.execute(select(Worker).where(Worker.team_id == team_id))
    return list(res.scalars().all())


async def delete_by_user_id(session: AsyncSession, user_id: int) -> None:
    await session.execute(delete(Worker).where(Worker.user_id == user_id))


async def delete_by_team(session: AsyncSession, team_id: int) -> None:
    await session.execute(
        delete(Worker).where(Worker.team_id == team_id)
    )
