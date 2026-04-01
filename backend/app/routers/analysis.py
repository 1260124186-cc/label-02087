"""分析路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import ApiResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/analysis", tags=["分析统计"])


@router.get("/{file_id}/protocol-stats", response_model=ApiResponse)
async def get_protocol_stats(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取协议分布统计"""
    service = AnalysisService(db)
    stats = await service.get_protocol_stats(file_id)

    return ApiResponse(
        success=True,
        message="获取成功",
        data=[s.model_dump() for s in stats]
    )


@router.get("/{file_id}/traffic-timeline", response_model=ApiResponse)
async def get_traffic_timeline(
    file_id: int,
    interval: float = Query(1.0, ge=0.1, le=60.0, description="时间间隔（秒）"),
    db: AsyncSession = Depends(get_db)
):
    """获取流量时间线"""
    service = AnalysisService(db)
    timeline = await service.get_traffic_timeline(file_id, interval)

    return ApiResponse(
        success=True,
        message="获取成功",
        data=[t.model_dump() for t in timeline]
    )


@router.get("/{file_id}/top-talkers", response_model=ApiResponse)
async def get_top_talkers(
    file_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取 Top 通信节点"""
    service = AnalysisService(db)
    talkers = await service.get_top_talkers(file_id, limit)

    return ApiResponse(
        success=True,
        message="获取成功",
        data=[t.model_dump() for t in talkers]
    )


@router.get("/{file_id}/diagnosis", response_model=ApiResponse)
async def get_diagnosis(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取智能诊断建议"""
    service = AnalysisService(db)
    diagnosis = await service.get_diagnosis(file_id)

    return ApiResponse(
        success=True,
        message="获取成功",
        data=[d.model_dump() for d in diagnosis]
    )
