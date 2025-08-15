from fastapi import Depends
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import get_session
from app.models.base import Base
from app.models.access_token_class import AccessToken


async def get_access_token_db(
    session: AsyncSession = Depends(get_session),
):  
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
