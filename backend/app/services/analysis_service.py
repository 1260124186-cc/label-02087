"""分析服务层"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.schemas import ProtocolStat, TrafficPoint, TopTalker, DiagnosisItem
from app.services.packet_service import PacketService
from app.utils.protocol_analyzer import ProtocolAnalyzer


class AnalysisService:
    """分析服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.packet_service = PacketService(db)

    async def _get_analyzer(self, file_id: int) -> ProtocolAnalyzer:
        """获取分析器实例"""
        packets = await self.packet_service.get_all_packets_data(file_id)
        return ProtocolAnalyzer(packets)

    async def get_protocol_stats(self, file_id: int) -> List[ProtocolStat]:
        """获取协议分布统计"""
        analyzer = await self._get_analyzer(file_id)
        result = analyzer.get_protocol_stats()
        logger.info(f"Protocol stats for file {file_id}: {len(result)} protocols")
        return result

    async def get_traffic_timeline(self, file_id: int, interval: float = 1.0) -> List[TrafficPoint]:
        """获取流量时间线"""
        analyzer = await self._get_analyzer(file_id)
        result = analyzer.get_traffic_timeline(interval)
        logger.info(f"Traffic timeline for file {file_id}: {len(result)} points")
        return result

    async def get_top_talkers(self, file_id: int, limit: int = 10) -> List[TopTalker]:
        """获取 Top 通信节点"""
        analyzer = await self._get_analyzer(file_id)
        result = analyzer.get_top_talkers(limit)
        logger.info(f"Top talkers for file {file_id}: {len(result)} IPs")
        return result

    async def get_diagnosis(self, file_id: int) -> List[DiagnosisItem]:
        """获取智能诊断建议"""
        analyzer = await self._get_analyzer(file_id)
        result = analyzer.get_diagnosis()
        logger.info(f"Diagnosis for file {file_id}: {len(result)} items")
        return result
