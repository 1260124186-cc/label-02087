# NetDoctor - 网络报文离线分析系统

## How to Run

### 环境要求
- Docker & Docker Compose
- SQLite 3（用于初始化数据库）

### 启动步骤

```bash
# 1. 初始化数据库
sqlite3 backend/netdoctor.db < backend/schema.sql

# 2. 启动所有服务（前端 + 后端）
docker compose up -d --build

# 3. 查看服务状态
docker compose ps
```

### 停止服务

```bash
docker compose down
```


## Services

| 服务 | 端口 | 地址 |
|------|------|------|
| 前端管理端 | 8081 | http://localhost:8081 |
| 后端 API | 8082 | http://localhost:8082 |
| API 文档 | 8082 | http://localhost:8082/docs |

## 测试账号

本系统无需登录认证，直接访问前端页面即可使用全部功能。

### 测试文件

项目提供测试用 PCAP 文件：`frontend-admin/data/test_capture.pcap`，包含 25 个报文（TCP/HTTP/DNS/ICMP/ARP/UDP），可用于测试系统功能。


## 题目内容

“你现在是一名全栈开发专家，精通 Python 后端和 Vue 前端开发。你将协助我开发一个名为 NetDoctor  的网络报文离线分析系统。
核心原则：
严谨性：  代码必须有错误处理，变量命名规范。
模块化：  代码要分层（路由层、服务层、工具层）。
AI 优先：  在后端处理中，优先考虑如何将数据结构化，以便前端能通过简单的 JSON 调用实现复杂的诊断逻辑。
循序渐进：  如果我要求的功能太复杂，你不要一次性输出几万行代码，请分模块、分文件输出，并告诉我文件路径。”

---

## 项目介绍

一个基于 Python + Vue 3 的网络报文离线分析工具，支持 PCAP/PCAPNG 文件解析、协议统计和智能诊断。

## 技术栈

### 后端
- FastAPI - 高性能 Web 框架
- Scapy - 网络报文解析
- SQLite + SQLAlchemy - 数据存储
- Pydantic - 数据校验

### 前端
- Vue 3 + Composition API
- Vite - 构建工具
- Element Plus - UI 组件库
- Pinia - 状态管理
- ECharts - 图表可视化
- Axios - HTTP 客户端

## 功能特性

- [x] PCAP/PCAPNG/CAP 文件上传解析（最大 100MB）
- [x] 文件列表管理（查看状态、删除）
- [x] 报文列表展示（分页浏览）
- [x] 报文过滤（按协议、源/目的 IP）
- [x] 报文详情查看（协议分层解析）
- [x] 原始数据 Hex 视图
- [x] 协议分布统计饼图
- [x] 流量时间线图表
- [x] Top 通信节点排行
- [x] 智能诊断建议（DNS/ICMP/ARP 异常检测）

## 项目结构

```
├── backend/                    # Python 后端
│   ├── app/                    # 应用代码
│   │   ├── routers/            # 路由层
│   │   ├── services/           # 服务层
│   │   ├── utils/              # 工具层
│   │   └── models/             # 数据模型
│   ├── uploads/                # 上传文件目录
│   ├── logs/                   # 日志目录
│   ├── Dockerfile
│   ├── requirements.txt
│   └── schema.sql              # 数据库初始化脚本
├── frontend-admin/             # Vue 前端（管理端）
│   ├── src/
│   │   ├── api/                # API 调用
│   │   ├── components/         # 组件
│   │   ├── views/              # 页面
│   │   ├── stores/             # Pinia 状态
│   │   └── styles/             # 样式
│   ├── data/                   # 测试数据
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── docs/                       # 设计文档
│   └── project_design.md
├── docker-compose.yml          # Docker 编排配置
└── README.md
```

## License

MIT
