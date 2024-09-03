from starlette.requests import Request
import time
from src.logger import logger


# @app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_extra =  {
        'method': request.method,
        'url': request.url.path,
        'query': dict(request.query_params),
    }
    if not log_extra['query']:
        del log_extra['query']
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(log_extra, extra=log_extra)
        logger.exception(e)
        raise
    else:
        process_time = round(time.time() - start_time, 2)
        log_extra['process_time'] = process_time
        logger.info(log_extra, extra=log_extra)
    return response