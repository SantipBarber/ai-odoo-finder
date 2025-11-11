from fastapi import APIRouter, Depends
from typing import List
from ...schemas import ModuleRead
from ...services.search_service import search_modules

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=List[ModuleRead])
def search(q: str):
    return search_modules(q)


