import time
import logging
from fastapi import Request

logger = logging.getLogger("request")


async def log_request(request: Request):
    start_time = time.time()

    yield  # execute endpoint

    duration = round(time.time() - start_time, 4)

    logger.info(
        "%s %s | status=%s | duration=%ss",
        request.method,
        request.url.path,
        request.scope["route"].status_code if "route" in request.scope else "N/A",
        duration,
    )
