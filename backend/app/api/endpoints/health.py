from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz():
    return {"status": "ok"}


