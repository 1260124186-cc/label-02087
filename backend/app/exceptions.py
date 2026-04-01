"""全局异常处理"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    """应用基础异常"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class FileNotFoundError(AppException):
    """文件不存在"""
    def __init__(self, file_id: int):
        super().__init__(f"文件不存在: {file_id}", 404)


class FileParseError(AppException):
    """文件解析失败"""
    def __init__(self, reason: str):
        super().__init__(f"文件解析失败: {reason}", 400)


class InvalidFileTypeError(AppException):
    """无效文件类型"""
    def __init__(self, filename: str):
        super().__init__(f"不支持的文件类型: {filename}", 400)


class FileTooLargeError(AppException):
    """文件过大"""
    def __init__(self, size: int, max_size: int):
        super().__init__(f"文件过大: {size} bytes, 最大允许 {max_size} bytes", 413)


async def app_exception_handler(request: Request, exc: AppException):
    """应用异常处理器"""
    logger.warning(f"AppException: {exc.message} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.code,
        content={"success": False, "message": exc.message, "data": None}
    )


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"Unhandled Exception: {str(exc)} | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "服务器内部错误", "data": None}
    )
