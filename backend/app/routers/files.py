"""文件管理路由"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database import get_db
from app.models.schemas import ApiResponse, CaptureFileResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/api/files", tags=["文件管理"])


@router.post("/upload", response_model=ApiResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传 PCAP 文件"""
    logger.info(f"Uploading file: {file.filename}")

    content = await file.read()
    service = FileService(db)
    result = await service.upload_file(file.filename, content)

    return ApiResponse(
        success=True,
        message="文件上传成功",
        data=result.model_dump()
    )


@router.get("", response_model=ApiResponse)
async def get_files(db: AsyncSession = Depends(get_db)):
    """获取文件列表"""
    service = FileService(db)
    files = await service.get_files()

    return ApiResponse(
        success=True,
        message="获取成功",
        data=[f.model_dump() for f in files]
    )


@router.get("/{file_id}", response_model=ApiResponse)
async def get_file(file_id: int, db: AsyncSession = Depends(get_db)):
    """获取文件详情"""
    service = FileService(db)
    file = await service.get_file(file_id)

    return ApiResponse(
        success=True,
        message="获取成功",
        data=file.model_dump()
    )


@router.delete("/{file_id}", response_model=ApiResponse)
async def delete_file(file_id: int, db: AsyncSession = Depends(get_db)):
    """删除文件"""
    logger.info(f"Deleting file: {file_id}")

    service = FileService(db)
    await service.delete_file(file_id)

    return ApiResponse(
        success=True,
        message="删除成功",
        data=None
    )
