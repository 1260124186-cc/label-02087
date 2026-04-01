"""协议分析工具"""
from collections import defaultdict
from typing import List
from app.models.schemas import ProtocolStat, TrafficPoint, TopTalker, DiagnosisItem


class ProtocolAnalyzer:
    """协议分析器"""

    def __init__(self, packets: List[dict]):
        self.packets = packets

    def get_protocol_stats(self) -> List[ProtocolStat]:
        """获取协议分布统计"""
        protocol_data = defaultdict(lambda: {"count": 0, "bytes": 0})
        total_count = len(self.packets)

        for pkt in self.packets:
            proto = pkt.get("protocol", "Unknown")
            protocol_data[proto]["count"] += 1
            protocol_data[proto]["bytes"] += pkt.get("length", 0)

        result = []
        for proto, data in sorted(protocol_data.items(), key=lambda x: x[1]["count"], reverse=True):
            result.append(ProtocolStat(
                protocol=proto,
                count=data["count"],
                percentage=round(data["count"] / total_count * 100, 2) if total_count > 0 else 0,
                total_bytes=data["bytes"]
            ))

        return result

    def get_traffic_timeline(self, interval: float = 1.0) -> List[TrafficPoint]:
        """获取流量时间线"""
        if not self.packets:
            return []

        # 按时间戳排序
        sorted_packets = sorted(
            [p for p in self.packets if p.get("timestamp")],
            key=lambda x: x["timestamp"]
        )

        if not sorted_packets:
            return []

        start_time = sorted_packets[0]["timestamp"]
        timeline = defaultdict(lambda: {"count": 0, "bytes": 0})

        for pkt in sorted_packets:
            # 计算时间槽
            slot = int((pkt["timestamp"] - start_time) / interval)
            timeline[slot]["count"] += 1
            timeline[slot]["bytes"] += pkt.get("length", 0)

        result = []
        for slot in sorted(timeline.keys()):
            result.append(TrafficPoint(
                timestamp=start_time + slot * interval,
                packet_count=timeline[slot]["count"],
                bytes_count=timeline[slot]["bytes"]
            ))

        return result

    def get_top_talkers(self, limit: int = 10) -> List[TopTalker]:
        """获取 Top 通信节点"""
        ip_stats = defaultdict(lambda: {"count": 0, "sent": 0, "received": 0})

        for pkt in self.packets:
            src_ip = pkt.get("src_ip")
            dst_ip = pkt.get("dst_ip")
            length = pkt.get("length", 0)

            if src_ip:
                ip_stats[src_ip]["count"] += 1
                ip_stats[src_ip]["sent"] += length

            if dst_ip:
                ip_stats[dst_ip]["count"] += 1
                ip_stats[dst_ip]["received"] += length

        # 按报文数量排序
        sorted_ips = sorted(ip_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:limit]

        return [
            TopTalker(
                ip=ip,
                packet_count=stats["count"],
                bytes_sent=stats["sent"],
                bytes_received=stats["received"]
            )
            for ip, stats in sorted_ips
        ]

    def get_diagnosis(self) -> List[DiagnosisItem]:
        """获取智能诊断建议"""
        diagnosis = []

        if not self.packets:
            diagnosis.append(DiagnosisItem(
                level="warning",
                category="数据",
                title="无报文数据",
                description="抓包文件中没有可分析的报文",
                suggestion="请确认抓包文件是否正确"
            ))
            return diagnosis

        # 统计数据
        protocol_stats = self.get_protocol_stats()
        protocol_map = {p.protocol: p for p in protocol_stats}
        total_packets = len(self.packets)

        # 1. 检查重传（简化版：检查 TCP 报文比例）
        tcp_stat = protocol_map.get("TCP")
        if tcp_stat and tcp_stat.percentage > 80:
            diagnosis.append(DiagnosisItem(
                level="info",
                category="协议分布",
                title="TCP 流量占比较高",
                description=f"TCP 报文占比 {tcp_stat.percentage}%，表明主要是面向连接的通信",
                suggestion="可进一步分析 TCP 会话和重传情况"
            ))

        # 2. 检查 DNS 查询
        dns_stat = protocol_map.get("DNS")
        if dns_stat:
            if dns_stat.count > total_packets * 0.1:
                diagnosis.append(DiagnosisItem(
                    level="warning",
                    category="DNS",
                    title="DNS 查询较多",
                    description=f"DNS 报文 {dns_stat.count} 个，占比 {dns_stat.percentage}%",
                    suggestion="检查是否存在 DNS 解析问题或 DNS 放大攻击"
                ))
            else:
                diagnosis.append(DiagnosisItem(
                    level="info",
                    category="DNS",
                    title="DNS 活动正常",
                    description=f"检测到 {dns_stat.count} 个 DNS 报文",
                    suggestion=None
                ))

        # 3. 检查 ICMP
        icmp_stat = protocol_map.get("ICMP")
        if icmp_stat and icmp_stat.count > 50:
            diagnosis.append(DiagnosisItem(
                level="warning",
                category="ICMP",
                title="ICMP 报文较多",
                description=f"检测到 {icmp_stat.count} 个 ICMP 报文",
                suggestion="检查是否存在网络探测或 Ping 洪水攻击"
            ))

        # 4. 检查 ARP
        arp_stat = protocol_map.get("ARP")
        if arp_stat and arp_stat.count > 100:
            diagnosis.append(DiagnosisItem(
                level="warning",
                category="ARP",
                title="ARP 报文异常",
                description=f"检测到 {arp_stat.count} 个 ARP 报文",
                suggestion="检查是否存在 ARP 欺骗或网络环路"
            ))

        # 5. 流量分布
        top_talkers = self.get_top_talkers(3)
        if top_talkers:
            top_ip = top_talkers[0]
            if top_ip.packet_count > total_packets * 0.5:
                diagnosis.append(DiagnosisItem(
                    level="info",
                    category="流量分布",
                    title="流量集中",
                    description=f"IP {top_ip.ip} 产生了 {top_ip.packet_count} 个报文，占总流量 {round(top_ip.packet_count/total_packets*100, 1)}%",
                    suggestion="该 IP 可能是主要通信节点或存在异常流量"
                ))

        # 6. 总体评估
        if len(diagnosis) == 0:
            diagnosis.append(DiagnosisItem(
                level="info",
                category="总体",
                title="流量正常",
                description=f"共分析 {total_packets} 个报文，未发现明显异常",
                suggestion=None
            ))

        return diagnosis
