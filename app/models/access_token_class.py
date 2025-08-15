from fastapi import Depends
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTable
from sqlalchemy import Integer, ForeignKey, Column, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AccessToken(Base, SQLAlchemyBaseAccessTokenTable[int]):
    id = None
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="cascade"),
        nullable=False,
    )
