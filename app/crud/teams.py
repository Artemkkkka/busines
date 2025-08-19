from typing import Iterable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException
from app.models.team import Team


async def get(session: AsyncSession, team_id: int) -> Team | None:
    return await session.get(Team, team_id)


async def get_or_404(session: AsyncSession, team_id: int) -> Team:
    team = await get(session, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


async def list_all(session: AsyncSession) -> list[Team]:
    res = await session.execute(select(Team))
    return list(res.scalars().all())


async def create(session: AsyncSession, *, name: str, code: str, owner_id: int | None) -> Team:
    team = Team(name=name, code=code, owner_id=owner_id)
    session.add(team)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Team code already exists")
    return team


async def update(session: AsyncSession, team: Team, *, name: str | None = None, code: str | None = None) -> Team:
    if name is not None:
        team.name = name
    if code is not None:
        team.code = code
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Team code already exists")
    return team


async def delete(session: AsyncSession, team: Team) -> None:
    await session.delete(team)


async def list_by_ids(session: AsyncSession, ids: Iterable[int]) -> list[Team]:
    res = await session.execute(select(Team).where(Team.id.in_(list(ids))))
    return list(res.scalars().all())
