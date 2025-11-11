from fastapi import APIRouter

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("/")
def list_modules():
    return []


