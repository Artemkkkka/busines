from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=3, max_length=64)


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    code: Optional[str] = Field(default=None, min_length=3, max_length=64)


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    owner_id: Optional[int] = None
