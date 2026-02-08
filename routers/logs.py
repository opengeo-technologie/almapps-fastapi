from fastapi import APIRouter, HTTPException, Query
from ..utils.log_reader import read_logs

router = APIRouter(prefix="/logs", tags=["logs"])

LOG_FILE = "backend1/logs/app.log"


@router.get("/")
async def get_logs(
    limit: int = Query(100, ge=1, le=1000),
    level: str | None = Query(None, description="INFO, ERROR, WARNING"),
):
    try:
        return {
            "count": limit,
            "logs": read_logs(LOG_FILE, limit=limit, level=level),
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Log file not found")
