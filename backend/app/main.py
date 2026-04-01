"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.config import settings
from app.exceptions import AppException, app_exception_handler, global_exception_handler
from app.routers import files, packets, analysis

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG"
)

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    description="网络报文离线分析系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://127.0.0.1:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 注册路由
app.include_router(files.router)
app.include_router(packets.router)
app.include_router(analysis.router)


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "app": settings.APP_NAME}


@app.on_event("startup")
async def startup():
    """应用启动"""
    logger.info(f"{settings.APP_NAME} starting...")
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")


@app.on_event("shutdown")
async def shutdown():
    """应用关闭"""
    logger.info(f"{settings.APP_NAME} shutting down...")
