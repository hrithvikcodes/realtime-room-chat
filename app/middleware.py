import time
from fastapi import Request
from app.logger import get_logger

logger = get_logger("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round(((time.time() - start_time) * 1000), 2)
    logger.info(
        "HTTP Request",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration_ms": duration
        }
    )
    return response