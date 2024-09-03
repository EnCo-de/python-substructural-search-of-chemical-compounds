from starlette.requests import Request
import time
from src.logger import logger


# @app.middleware("http")
async def log_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    log_extra =  {
        'method': request.method,
        'url': request.url.path,
        'query': request.query_params.items(),
        'process_time': round(process_time, 2),
    }
    logger.info(log_extra, extra=log_extra)
    return response