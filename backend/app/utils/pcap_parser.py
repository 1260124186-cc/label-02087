"""PCAP 文件解析工具"""
import json
from pathlib import Path
from typing import Generator, Optional
from scapy.all import rdpcap, Packet, IP, IPv6, TCP, UDP, ICMP, DNS, ARP, Ether
from loguru import logger


class PcapParser:
    """PCAP 文件解析器"""

    PROTOCOL_MAP = {
        6: "TCP",
        17: "UDP",
        1: "ICMP",
        58: "ICMPv6",
    }

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._packets = None

    def load(self) -> int:
        """加载 PCAP 文件，返回报文数量"""
        try:
            self._packets = rdpcap(str(self.file_path))
            count = len(self._packets)
            logger.info(f"Loaded {count} packets from {self.file_path}")
            return count
        except Exception as e:
            logger.error(f"Failed to load PCAP: {e}")
            raise

    def parse_packets(self) -> Generator[dict, None, None]:
        """解析所有报文，生成器方式返回"""
        if self._packets is None:
            self.load()

        for idx, pkt in enumerate(self._packets, start=1):
            yield self._parse_single_packet(pkt, idx)

    def _parse_single_packet(self, pkt: Packet, packet_no: int) -> dict:
        """解析单个报文"""
        result = {
            "packet_no": packet_no,
            "timestamp": float(pkt.time) if hasattr(pkt, 'time') else None,
            "length": len(pkt),
            "raw_hex": bytes(pkt).hex(),
            "src_ip": None,
            "dst_ip": None,
            "src_port": None,
            "dst_port": None,
            "protocol": "Unknown",
            "layers": {}
        }

        # 解析以太网层
        if Ether in pkt:
            result["layers"]["Ethernet"] = {
                "src_mac": pkt[Ether].src,
                "dst_mac": pkt[Ether].dst,
                "type": hex(pkt[Ether].type)
            }

        # 解析 ARP
        if ARP in pkt:
            result["protocol"] = "ARP"
            result["layers"]["ARP"] = {
                "op": "request" if pkt[ARP].op == 1 else "reply",
                "src_ip": pkt[ARP].psrc,
                "dst_ip": pkt[ARP].pdst,
                "src_mac": pkt[ARP].hwsrc,
                "dst_mac": pkt[ARP].hwdst
            }
            result["src_ip"] = pkt[ARP].psrc
            result["dst_ip"] = pkt[ARP].pdst
            return result

        # 解析 IP 层
        if IP in pkt:
            ip_layer = pkt[IP]
            result["src_ip"] = ip_layer.src
            result["dst_ip"] = ip_layer.dst
            result["protocol"] = self.PROTOCOL_MAP.get(ip_layer.proto, f"IP({ip_layer.proto})")
            result["layers"]["IP"] = {
                "version": ip_layer.version,
                "ihl": ip_layer.ihl,
                "tos": ip_layer.tos,
                "len": ip_layer.len,
                "id": ip_layer.id,
                "flags": str(ip_layer.flags),
                "frag": ip_layer.frag,
                "ttl": ip_layer.ttl,
                "proto": ip_layer.proto,
                "src": ip_layer.src,
                "dst": ip_layer.dst
            }
        elif IPv6 in pkt:
            ip_layer = pkt[IPv6]
            result["src_ip"] = ip_layer.src
            result["dst_ip"] = ip_layer.dst
            result["protocol"] = "IPv6"
            result["layers"]["IPv6"] = {
                "version": ip_layer.version,
                "tc": ip_layer.tc,
                "fl": ip_layer.fl,
                "plen": ip_layer.plen,
                "nh": ip_layer.nh,
                "hlim": ip_layer.hlim,
                "src": ip_layer.src,
                "dst": ip_layer.dst
            }

        # 解析传输层
        if TCP in pkt:
            tcp_layer = pkt[TCP]
            result["src_port"] = tcp_layer.sport
            result["dst_port"] = tcp_layer.dport
            result["protocol"] = "TCP"
            result["layers"]["TCP"] = {
                "sport": tcp_layer.sport,
                "dport": tcp_layer.dport,
                "seq": tcp_layer.seq,
                "ack": tcp_layer.ack,
                "flags": str(tcp_layer.flags),
                "window": tcp_layer.window,
                "urgptr": tcp_layer.urgptr
            }
            # 识别应用层协议
            result["protocol"] = self._detect_app_protocol(tcp_layer.sport, tcp_layer.dport, "TCP")

        elif UDP in pkt:
            udp_layer = pkt[UDP]
            result["src_port"] = udp_layer.sport
            result["dst_port"] = udp_layer.dport
            result["protocol"] = "UDP"
            result["layers"]["UDP"] = {
                "sport": udp_layer.sport,
                "dport": udp_layer.dport,
                "len": udp_layer.len
            }
            result["protocol"] = self._detect_app_protocol(udp_layer.sport, udp_layer.dport, "UDP")

        elif ICMP in pkt:
            icmp_layer = pkt[ICMP]
            result["protocol"] = "ICMP"
            result["layers"]["ICMP"] = {
                "type": icmp_layer.type,
                "code": icmp_layer.code,
                "id": getattr(icmp_layer, 'id', None),
                "seq": getattr(icmp_layer, 'seq', None)
            }

        # 解析 DNS
        if DNS in pkt:
            dns_layer = pkt[DNS]
            result["protocol"] = "DNS"
            result["layers"]["DNS"] = {
                "id": dns_layer.id,
                "qr": dns_layer.qr,
                "opcode": dns_layer.opcode,
                "qdcount": dns_layer.qdcount,
                "ancount": dns_layer.ancount
            }
            # 提取查询域名
            if dns_layer.qd:
                result["layers"]["DNS"]["query"] = dns_layer.qd.qname.decode() if isinstance(dns_layer.qd.qname, bytes) else str(dns_layer.qd.qname)

        return result

    def _detect_app_protocol(self, sport: int, dport: int, transport: str) -> str:
        """根据端口识别应用层协议"""
        well_known_ports = {
            80: "HTTP",
            443: "HTTPS",
            22: "SSH",
            21: "FTP",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            110: "POP3",
            143: "IMAP",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            27017: "MongoDB",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt",
        }

        for port in (sport, dport):
            if port in well_known_ports:
                return well_known_ports[port]

        return transport

    def get_packet_count(self) -> int:
        """获取报文数量"""
        if self._packets is None:
            self.load()
        return len(self._packets)
