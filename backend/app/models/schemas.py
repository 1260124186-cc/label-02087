"""Pydantic 数据模型"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ============ 通用响应 ============

class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


# ============ 文件相关 ============

class CaptureFileBase(BaseModel):
    """抓包文件基础模型"""
    original_name: str
    file_size: int


class CaptureFileCreate(CaptureFileBase):
    """创建抓包文件"""
    filename: str


class CaptureFileResponse(CaptureFileBase):
    """抓包文件响应"""
    id: int
    filename: str
    upload_time: datetime
    status: str
    packet_count: int

    class Config:
        from_attributes = True


# ============ 报文相关 ============

class PacketBase(BaseModel):
    """报文基础模型"""
    packet_no: int
    timestamp: Optional[float] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    length: int


class PacketListItem(PacketBase):
    """报文列表项"""
    id: int

    class Config:
        from_attributes = True


class PacketDetail(PacketBase):
    """报文详情"""
    id: int
    file_id: int
    raw_hex: Optional[str] = None
    layers: Optional[dict] = None

    class Config:
        from_attributes = True


class PacketFilter(BaseModel):
    """报文过滤条件"""
    protocol: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None


# ============ 分析相关 ============

class ProtocolStat(BaseModel):
    """协议统计"""
    protocol: str
    count: int
    percentage: float
    total_bytes: int


class TrafficPoint(BaseModel):
    """流量时间点"""
    timestamp: float
    packet_count: int
    bytes_count: int


class TopTalker(BaseModel):
    """Top 通信节点"""
    ip: str
    packet_count: int
    bytes_sent: int
    bytes_received: int


class DiagnosisItem(BaseModel):
    """诊断项"""
    level: str = Field(..., description="info/warning/error")
    category: str
    title: str
    description: str
    suggestion: Optional[str] = None
