CAPTURES = """
CREATE TABLE IF NOT EXISTS captures (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  original_name TEXT NOT NULL,
  stored_path TEXT NOT NULL,
  file_type TEXT NOT NULL,
  file_size INTEGER NOT NULL,
  packet_count INTEGER NOT NULL DEFAULT 0,
  total_bytes INTEGER NOT NULL DEFAULT 0,
  duration_seconds REAL NOT NULL DEFAULT 0,
  started_at TEXT,
  ended_at TEXT,
  uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  analysis_time TEXT,
  status TEXT NOT NULL DEFAULT 'Uploaded',
  error_message TEXT
);
"""

PACKETS = """
CREATE TABLE IF NOT EXISTS packets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  capture_id INTEGER NOT NULL,
  number INTEGER NOT NULL,
  timestamp TEXT NOT NULL,
  src_ip TEXT,
  src_port TEXT,
  dst_ip TEXT,
  dst_port TEXT,
  protocol TEXT NOT NULL,
  length INTEGER NOT NULL,
  details_json TEXT NOT NULL,
  FOREIGN KEY(capture_id) REFERENCES captures(id) ON DELETE CASCADE
);
"""

SETTINGS = """
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
"""

AI_SUMMARIES = """
CREATE TABLE IF NOT EXISTS ai_summaries (
  capture_id INTEGER PRIMARY KEY,
  summary TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(capture_id) REFERENCES captures(id) ON DELETE CASCADE
);
"""

DEFAULT_SETTINGS = {
    "api_base": "https://api.deepseek.com",
    "model": "deepseek-v4-pro",
    "streaming": "true",
    "api_key": "",
}
