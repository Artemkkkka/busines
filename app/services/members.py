from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import workers as crud_workers
from app.crud import teams as crud_teams
from app.utils import team_utils
from app.models.team import TeamRole
from app.models.user import User


async def add_member(
    session: AsyncSession, *, actor: User, team_id: int, user_id: int, role: TeamRole
):
    await crud_teams.get_or_404(session, team_id)
    await team_utils.require_superuser_or_team_admin(session, actor, team_id)

    m = await crud_workers.ensure_exists(session, user_id)
    # один worker -> одна команда: запретим перенос из другой команды
    if m.team_id is not None and m.team_id != team_id:
        raise HTTPException(status_code=409, detail="User already belongs to another team")

    m.team_id = team_id
    m.role_in_team = role

    await session.commit()
    await session.refresh(m)
    return m


async def change_member_role(
    session: AsyncSession, *, actor: User, team_id: int, user_id: int, role: TeamRole
):
    await crud_teams.get_or_404(session, team_id)
    await team_utils.require_superuser_or_team_admin(session, actor, team_id)

    m = await crud_workers.get_by_user_id(session, user_id)
    if not m or m.team_id != team_id:
        raise HTTPException(status_code=404, detail="Member not in this team")

    m.role_in_team = role
    await session.commit()
    await session.refresh(m)
    return m


async def remove_member(session: AsyncSession, *, actor: User, team_id: int, user_id: int) -> None:
    await crud_teams.get_or_404(session, team_id)
    await team_utils.require_superuser_or_team_admin(session, actor, team_id)

    m = await crud_workers.get_by_user_id(session, user_id)
    if not m or m.team_id != team_id:
        return

    await crud_workers.delete_by_user_id(session, user_id)

    await session.commit()
