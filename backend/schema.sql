-- NetDoctor 数据库初始化脚本

-- 抓包文件表
CREATE TABLE IF NOT EXISTS capture_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    packet_count INTEGER DEFAULT 0
);

-- 报文表
CREATE TABLE IF NOT EXISTS packets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    packet_no INTEGER NOT NULL,
    timestamp REAL,
    src_ip VARCHAR(45),
    dst_ip VARCHAR(45),
    src_port INTEGER,
    dst_port INTEGER,
    protocol VARCHAR(50),
    length INTEGER,
    raw_hex TEXT,
    layers TEXT,
    FOREIGN KEY (file_id) REFERENCES capture_files(id) ON DELETE CASCADE
);

-- 分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    analysis_type VARCHAR(100) NOT NULL,
    result_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES capture_files(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_packets_file_id ON packets(file_id);
CREATE INDEX IF NOT EXISTS idx_packets_protocol ON packets(protocol);
CREATE INDEX IF NOT EXISTS idx_analysis_file_id ON analysis_results(file_id);
