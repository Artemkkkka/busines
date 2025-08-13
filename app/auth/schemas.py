from typing import Optional
from pydantic import Field

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    global_role: str = "user"


class UserCreate(schemas.BaseUserCreate):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(schemas.BaseUserUpdate):
    global_role: Optional[str] = None
