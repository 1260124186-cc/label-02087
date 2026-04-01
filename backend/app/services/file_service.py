"""文件服务层"""
import uuid
import json
from pathlib import Path
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.config import settings
from app.models.schemas import CaptureFileResponse
from app.utils.pcap_parser import PcapParser
from app.exceptions import FileNotFoundError, FileParseError, InvalidFileTypeError, FileTooLargeError


class FileService:
    """文件服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_file(self, filename: str, content: bytes) -> CaptureFileResponse:
        """上传并解析文件"""
        # 验证文件类型
        suffix = Path(filename).suffix.lower()
        if suffix not in settings.ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(filename)

        # 验证文件大小
        if len(content) > settings.MAX_FILE_SIZE:
            raise FileTooLargeError(len(content), settings.MAX_FILE_SIZE)

        # 生成唯一文件名
        unique_name = f"{uuid.uuid4().hex}{suffix}"
        file_path = settings.UPLOAD_DIR / unique_name

        # 保存文件
        file_path.write_bytes(content)
        logger.info(f"File saved: {file_path}")

        # 创建数据库记录
        query = text("""
            INSERT INTO capture_files (filename, original_name, file_size, status)
            VALUES (:filename, :original_name, :file_size, :status)
        """)
        result = await self.db.execute(
            query,
            {
                "filename": unique_name,
                "original_name": filename,
                "file_size": len(content),
                "status": "parsing"
            }
        )
        await self.db.commit()

        # 获取插入的 ID
        file_id = result.lastrowid

        # 解析文件
        try:
            await self._parse_and_store_packets(file_id, file_path)
            await self._update_file_status(file_id, "completed")
        except Exception as e:
            logger.error(f"Parse failed: {e}")
            await self._update_file_status(file_id, "failed")
            raise FileParseError(str(e))

        return await self.get_file(file_id)

    async def _parse_and_store_packets(self, file_id: int, file_path: Path):
        """解析并存储报文"""
        parser = PcapParser(file_path)
        packet_count = 0

        for pkt_data in parser.parse_packets():
            query = text("""
                INSERT INTO packets (
                    file_id, packet_no, timestamp, src_ip, dst_ip,
                    src_port, dst_port, protocol, length, raw_hex, layers
                ) VALUES (
                    :file_id, :packet_no, :timestamp, :src_ip, :dst_ip,
                    :src_port, :dst_port, :protocol, :length, :raw_hex, :layers
                )
            """)
            await self.db.execute(query, {
                "file_id": file_id,
                "packet_no": pkt_data["packet_no"],
                "timestamp": pkt_data["timestamp"],
                "src_ip": pkt_data["src_ip"],
                "dst_ip": pkt_data["dst_ip"],
                "src_port": pkt_data["src_port"],
                "dst_port": pkt_data["dst_port"],
                "protocol": pkt_data["protocol"],
                "length": pkt_data["length"],
                "raw_hex": pkt_data["raw_hex"],
                "layers": json.dumps(pkt_data["layers"])
            })
            packet_count += 1

            # 每 100 条提交一次
            if packet_count % 100 == 0:
                await self.db.commit()

        await self.db.commit()

        # 更新报文数量
        await self.db.execute(
            text("UPDATE capture_files SET packet_count = :count WHERE id = :id"),
            {"count": packet_count, "id": file_id}
        )
        await self.db.commit()

        logger.info(f"Stored {packet_count} packets for file {file_id}")

    async def _update_file_status(self, file_id: int, status: str):
        """更新文件状态"""
        await self.db.execute(
            text("UPDATE capture_files SET status = :status WHERE id = :id"),
            {"status": status, "id": file_id}
        )
        await self.db.commit()

    async def get_file(self, file_id: int) -> CaptureFileResponse:
        """获取文件详情"""
        result = await self.db.execute(
            text("SELECT * FROM capture_files WHERE id = :id"),
            {"id": file_id}
        )
        row = result.fetchone()

        if not row:
            raise FileNotFoundError(file_id)

        return CaptureFileResponse(
            id=row.id,
            filename=row.filename,
            original_name=row.original_name,
            file_size=row.file_size,
            upload_time=row.upload_time,
            status=row.status,
            packet_count=row.packet_count
        )

    async def get_files(self) -> List[CaptureFileResponse]:
        """获取文件列表"""
        result = await self.db.execute(
            text("SELECT * FROM capture_files ORDER BY upload_time DESC")
        )
        rows = result.fetchall()

        return [
            CaptureFileResponse(
                id=row.id,
                filename=row.filename,
                original_name=row.original_name,
                file_size=row.file_size,
                upload_time=row.upload_time,
                status=row.status,
                packet_count=row.packet_count
            )
            for row in rows
        ]

    async def delete_file(self, file_id: int) -> bool:
        """删除文件"""
        file = await self.get_file(file_id)

        # 删除物理文件
        file_path = settings.UPLOAD_DIR / file.filename
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")

        # 删除数据库记录（级联删除报文）
        await self.db.execute(
            text("DELETE FROM packets WHERE file_id = :id"),
            {"id": file_id}
        )
        await self.db.execute(
            text("DELETE FROM capture_files WHERE id = :id"),
            {"id": file_id}
        )
        await self.db.commit()

        logger.info(f"Deleted file record: {file_id}")
        return True
