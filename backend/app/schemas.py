from pydantic import BaseModel
from typing import Optional


class ModuleBase(BaseModel):
    name: str
    summary: Optional[str] = None
    repository_url: Optional[str] = None
    quality_score: Optional[float] = None


class ModuleCreate(ModuleBase):
    pass


class ModuleRead(ModuleBase):
    id: int

    class Config:
        orm_mode = True


