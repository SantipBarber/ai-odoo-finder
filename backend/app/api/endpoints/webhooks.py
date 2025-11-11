from fastapi import APIRouter, Header

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/github")
def github_webhook(x_github_event: str = Header(default="")):
    return {"received": x_github_event}


