from typing import Annotated, Optional
from pydantic import EmailStr, StringConstraints, BaseModel

from fastapi_users import schemas

Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserSelfUpdate(BaseModel):
    email: Optional[EmailStr] = None


class UserAdminUpdate(schemas.BaseUserUpdate):
    pass
