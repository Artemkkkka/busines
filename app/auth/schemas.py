from typing import Annotated, Optional
from pydantic import EmailStr, StringConstraints, ConfigDict

from fastapi_users import schemas

Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
