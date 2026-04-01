"""报文管理路由"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import ApiResponse, PacketFilter
from app.services.packet_service import PacketService

router = APIRouter(prefix="/api/packets", tags=["报文管理"])


@router.get("/{file_id}", response_model=ApiResponse)
async def get_packets(
    file_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    protocol: Optional[str] = None,
    src_ip: Optional[str] = None,
    dst_ip: Optional[str] = None,
    src_port: Optional[int] = None,
    dst_port: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取报文列表（分页）"""
    filters = PacketFilter(
        protocol=protocol,
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_port=src_port,
        dst_port=dst_port,
        min_length=min_length,
        max_length=max_length
    )

    service = PacketService(db)
    result = await service.get_packets(file_id, page, page_size, filters)

    return ApiResponse(
        success=True,
        message="获取成功",
        data=result.model_dump()
    )


@router.get("/{file_id}/{packet_no}", response_model=ApiResponse)
async def get_packet_detail(
    file_id: int,
    packet_no: int,
    db: AsyncSession = Depends(get_db)
):
    """获取报文详情"""
    service = PacketService(db)
    packet = await service.get_packet_detail(file_id, packet_no)

    return ApiResponse(
        success=True,
        message="获取成功",
        data=packet.model_dump()
    )
