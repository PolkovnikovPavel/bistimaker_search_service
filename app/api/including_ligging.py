import logging.handlers
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


def init_loger(app, name):
    class ErrorLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            start_time = time.time()
            client_ip = request.client.host
            method = request.method
            url = request.url.path
            query_params = dict(request.query_params)

            try:
                response = await call_next(request)
            except Exception as e:
                logger.error(f"Exception occurred: {e}", exc_info=True)
                raise e
            finally:
                process_time = time.time() - start_time
                logger.info(
                    f"Request completed: IP={client_ip}, Method={method}, URL={url}, StatusCode={response.status_code}, ProcessTime={process_time:.4f}s, QueryParams={query_params}")

            return response

    logging.basicConfig(
        level=logging.INFO,  # Уровень логирования
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат сообщения
        handlers=[
            # Файловый обработчик
            logging.handlers.RotatingFileHandler("app/logs/app.log", maxBytes=100*1024, backupCount=5, encoding='utf-8'),
            logging.StreamHandler()  # Обработчик для вывода в консоль (опционально)
        ]
    )
    logger = logging.getLogger(name)
    app.add_middleware(ErrorLoggingMiddleware)
    return logger



