import logging
import os
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from datetime import datetime

log_file = "api.log"

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, logger: logging.Logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = datetime.now()

        # 记录请求开始
        self.logger.info(f"开始处理请求: {request.method} {request.url}")

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = (datetime.now() - start_time).total_seconds()

            # 记录成功的请求
            self.logger.info(
                f"请求处理完成: {request.method} {request.url} "
                f"状态码: {response.status_code} "
                f"处理时间: {process_time:.3f}s"
            )

            return response

        except Exception as e:
            # 记录失败的请求，包含详细的错误信息和堆栈跟踪
            import traceback
            self.logger.error(
                f"请求处理异常: {request.method} {request.url}\n"
                f"错误类型: {type(e).__name__}\n"
                f"错误信息: {str(e)}\n"
                f"堆栈跟踪:\n{traceback.format_exc()}"
            )
            raise

def setup_logger():
    # 如果日志文件存在，则清理
    if os.path.exists(log_file):
        clean_logs()

    logger = logging.getLogger("api")
    logger.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 清除现有的处理器
    logger.handlers.clear()

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# 只保留前1000行
def clean_logs(max_lines=1000):
    with open(log_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    with open(log_file, "w", encoding="utf-8") as file:
        file.writelines(lines[-max_lines:])
