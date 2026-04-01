"""报文服务层"""
import json
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.config import settings
from app.models.schemas import PacketListItem, PacketDetail, PacketFilter, PaginatedResponse
from app.exceptions import FileNotFoundError


class PacketService:
    """报文服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_packets(
        self,
        file_id: int,
        page: int = 1,
        page_size: int = None,
        filters: PacketFilter = None
    ) -> PaginatedResponse:
        """获取报文列表（分页）"""
        page_size = page_size or settings.DEFAULT_PAGE_SIZE
        page_size = min(page_size, settings.MAX_PAGE_SIZE)
        offset = (page - 1) * page_size

        # 构建查询条件
        where_clauses = ["file_id = :file_id"]
        params = {"file_id": file_id}

        if filters:
            if filters.protocol:
                where_clauses.append("protocol = :protocol")
                params["protocol"] = filters.protocol
            if filters.src_ip:
                where_clauses.append("src_ip = :src_ip")
                params["src_ip"] = filters.src_ip
            if filters.dst_ip:
                where_clauses.append("dst_ip = :dst_ip")
                params["dst_ip"] = filters.dst_ip
            if filters.src_port:
                where_clauses.append("src_port = :src_port")
                params["src_port"] = filters.src_port
            if filters.dst_port:
                where_clauses.append("dst_port = :dst_port")
                params["dst_port"] = filters.dst_port
            if filters.min_length:
                where_clauses.append("length >= :min_length")
                params["min_length"] = filters.min_length
            if filters.max_length:
                where_clauses.append("length <= :max_length")
                params["max_length"] = filters.max_length

        where_sql = " AND ".join(where_clauses)

        # 查询总数
        count_result = await self.db.execute(
            text(f"SELECT COUNT(*) as cnt FROM packets WHERE {where_sql}"),
            params
        )
        total = count_result.fetchone().cnt

        # 查询数据
        query = text(f"""
            SELECT id, packet_no, timestamp, src_ip, dst_ip, src_port, dst_port, protocol, length
            FROM packets
            WHERE {where_sql}
            ORDER BY packet_no
            LIMIT :limit OFFSET :offset
        """)
        params["limit"] = page_size
        params["offset"] = offset

        result = await self.db.execute(query, params)
        rows = result.fetchall()

        items = [
            PacketListItem(
                id=row.id,
                packet_no=row.packet_no,
                timestamp=row.timestamp,
                src_ip=row.src_ip,
                dst_ip=row.dst_ip,
                src_port=row.src_port,
                dst_port=row.dst_port,
                protocol=row.protocol,
                length=row.length
            )
            for row in rows
        ]

        total_pages = (total + page_size - 1) // page_size

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    async def get_packet_detail(self, file_id: int, packet_no: int) -> PacketDetail:
        """获取报文详情"""
        result = await self.db.execute(
            text("SELECT * FROM packets WHERE file_id = :file_id AND packet_no = :packet_no"),
            {"file_id": file_id, "packet_no": packet_no}
        )
        row = result.fetchone()

        if not row:
            raise FileNotFoundError(f"Packet {packet_no} not found in file {file_id}")

        layers = json.loads(row.layers) if row.layers else {}

        return PacketDetail(
            id=row.id,
            file_id=row.file_id,
            packet_no=row.packet_no,
            timestamp=row.timestamp,
            src_ip=row.src_ip,
            dst_ip=row.dst_ip,
            src_port=row.src_port,
            dst_port=row.dst_port,
            protocol=row.protocol,
            length=row.length,
            raw_hex=row.raw_hex,
            layers=layers
        )

    async def get_all_packets_data(self, file_id: int) -> List[dict]:
        """获取所有报文数据（用于分析）"""
        result = await self.db.execute(
            text("""
                SELECT packet_no, timestamp, src_ip, dst_ip, src_port, dst_port, protocol, length
                FROM packets
                WHERE file_id = :file_id
                ORDER BY packet_no
            """),
            {"file_id": file_id}
        )
        rows = result.fetchall()

        return [
            {
                "packet_no": row.packet_no,
                "timestamp": row.timestamp,
                "src_ip": row.src_ip,
                "dst_ip": row.dst_ip,
                "src_port": row.src_port,
                "dst_port": row.dst_port,
                "protocol": row.protocol,
                "length": row.length
            }
            for row in rows
        ]
