import json
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path

from src.backend.db.schema import AI_SUMMARIES, CAPTURES, DEFAULT_SETTINGS, PACKETS, SETTINGS


class Repository:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init(self):
        with self.connect() as conn:
            conn.execute(CAPTURES)
            conn.execute(PACKETS)
            conn.execute(SETTINGS)
            conn.execute(AI_SUMMARIES)
            conn.executemany(
                "INSERT OR IGNORE INTO settings(key, value) VALUES(?, ?)",
                DEFAULT_SETTINGS.items(),
            )

    def create_capture(self, original_name, stored_path, file_size, file_type):
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO captures(original_name, stored_path, file_size, file_type)
                VALUES (?, ?, ?, ?)
                """,
                (original_name, stored_path, file_size, file_type),
            )
            return cur.lastrowid

    def list_captures(self, q="", status=""):
        sql = "SELECT * FROM captures WHERE 1=1"
        args = []
        if q:
            sql += " AND lower(original_name) LIKE ?"
            args.append(f"%{q.lower()}%")
        if status:
            sql += " AND status = ?"
            args.append(status)
        sql += " ORDER BY uploaded_at DESC, id DESC"
        with self.connect() as conn:
            return [dict(row) for row in conn.execute(sql, args)]

    def get_capture(self, capture_id):
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM captures WHERE id = ?", (capture_id,)).fetchone()
            return dict(row) if row else None

    def delete_capture(self, capture_id):
        capture = self.get_capture(capture_id)
        with self.connect() as conn:
            conn.execute("DELETE FROM captures WHERE id = ?", (capture_id,))
        return capture

    def update_status(self, capture_id, status, error_message=None):
        with self.connect() as conn:
            conn.execute(
                "UPDATE captures SET status = ?, error_message = ? WHERE id = ?",
                (status, error_message, capture_id),
            )

    def save_analysis(self, capture_id, packets):
        packets = list(packets)
        total_bytes = sum(packet["length"] for packet in packets)
        started_at = packets[0]["timestamp"] if packets else None
        ended_at = packets[-1]["timestamp"] if packets else None
        duration = self._duration_seconds(packets)
        with self.connect() as conn:
            conn.execute("DELETE FROM packets WHERE capture_id = ?", (capture_id,))
            conn.executemany(
                """
                INSERT INTO packets(
                  capture_id, number, timestamp, src_ip, src_port, dst_ip, dst_port,
                  protocol, length, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        capture_id,
                        p["number"],
                        p["timestamp"],
                        p.get("src_ip"),
                        p.get("src_port"),
                        p.get("dst_ip"),
                        p.get("dst_port"),
                        p["protocol"],
                        p["length"],
                        json.dumps(p.get("details", {})),
                    )
                    for p in packets
                ],
            )
            conn.execute(
                """
                UPDATE captures
                SET status = 'Completed', packet_count = ?, total_bytes = ?,
                    duration_seconds = ?, started_at = ?, ended_at = ?,
                    analysis_time = CURRENT_TIMESTAMP, error_message = NULL
                WHERE id = ?
                """,
                (len(packets), total_bytes, duration, started_at, ended_at, capture_id),
            )

    def list_packets(self, capture_id, filters):
        where = ["capture_id = ?"]
        args = [capture_id]
        q = filters.get("q")
        if q:
            where.append("(src_ip LIKE ? OR dst_ip LIKE ? OR src_port LIKE ? OR dst_port LIKE ? OR protocol LIKE ?)")
            args.extend([f"%{q}%"] * 5)
        for key, column in [("protocol", "protocol"), ("src_ip", "src_ip"), ("dst_ip", "dst_ip")]:
            if filters.get(key):
                where.append(f"{column} = ?")
                args.append(filters[key])
        if filters.get("port"):
            where.append("(src_port = ? OR dst_port = ?)")
            args.extend([filters["port"], filters["port"]])
        sort = "length" if filters.get("sort") == "length" else "timestamp"
        direction = "DESC" if filters.get("direction") == "desc" else "ASC"
        page = max(int(filters.get("page", 1)), 1)
        page_size = min(max(int(filters.get("page_size", 25)), 1), 100)
        offset = (page - 1) * page_size
        clause = " AND ".join(where)
        with self.connect() as conn:
            total = conn.execute(f"SELECT COUNT(*) FROM packets WHERE {clause}", args).fetchone()[0]
            rows = conn.execute(
                f"SELECT * FROM packets WHERE {clause} ORDER BY {sort} {direction} LIMIT ? OFFSET ?",
                args + [page_size, offset],
            )
            items = [self._packet(row) for row in rows]
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def get_packet(self, capture_id, number):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM packets WHERE capture_id = ? AND number = ?",
                (capture_id, number),
            ).fetchone()
            return self._packet(row) if row else None

    def stats(self, capture_id=None):
        captures = [self.get_capture(capture_id)] if capture_id else self.list_captures()
        captures = [c for c in captures if c]
        packet_rows = self._packet_rows(capture_id)
        protocols = Counter(row["protocol"] for row in packet_rows)
        src = Counter(row["src_ip"] for row in packet_rows if row["src_ip"])
        dst = Counter(row["dst_ip"] for row in packet_rows if row["dst_ip"])
        ports = Counter(row["dst_port"] for row in packet_rows if row["dst_port"])
        sizes = Counter(self._size_bucket(row["length"]) for row in packet_rows)
        trend = Counter(row["timestamp"][:19] for row in packet_rows)
        trend_bytes = Counter()
        protocol_trends = {}
        protocol_bytes = {}
        for row in packet_rows:
            bucket = row["timestamp"][:19]
            protocol = row["protocol"]
            trend_bytes[bucket] += row["length"]
            protocol_trends.setdefault(protocol, Counter())[bucket] += 1
            protocol_bytes.setdefault(protocol, Counter())[bucket] += row["length"]
        return {
            "summary": {
                "total_captures": len(captures),
                "total_packets": sum(c["packet_count"] for c in captures),
                "total_size": sum(c["file_size"] for c in captures),
                "completed": sum(1 for c in captures if c["status"] == "Completed"),
                "failed": sum(1 for c in captures if c["status"] == "Failed"),
                "source_ip_count": len(src),
                "destination_ip_count": len(dst),
            },
            "protocols": protocols.most_common(),
            "top_sources": src.most_common(8),
            "top_destinations": dst.most_common(8),
            "top_ports": ports.most_common(8),
            "packet_sizes": sizes.most_common(),
            "traffic_trend": sorted(trend.items()),
            "traffic_trend_bytes": sorted(trend_bytes.items()),
            "traffic_trend_by_protocol": {key: sorted(value.items()) for key, value in protocol_trends.items()},
            "traffic_trend_bytes_by_protocol": {key: sorted(value.items()) for key, value in protocol_bytes.items()},
        }

    def settings(self):
        with self.connect() as conn:
            return {row["key"]: row["value"] for row in conn.execute("SELECT * FROM settings")}

    def save_settings(self, values):
        allowed = {"api_base", "model", "streaming", "api_key"}
        with self.connect() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO settings(key, value) VALUES(?, ?)",
                [(k, str(v)) for k, v in values.items() if k in allowed],
            )
        return self.settings()

    def save_ai_summary(self, capture_id, summary):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO ai_summaries(capture_id, summary, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(capture_id) DO UPDATE SET
                  summary = excluded.summary,
                  updated_at = CURRENT_TIMESTAMP
                """,
                (capture_id, summary),
            )

    def get_ai_summary(self, capture_id):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT summary, updated_at FROM ai_summaries WHERE capture_id = ?",
                (capture_id,),
            ).fetchone()
            return dict(row) if row else None

    def _packet_rows(self, capture_id=None):
        sql = "SELECT * FROM packets"
        args = []
        if capture_id:
            sql += " WHERE capture_id = ?"
            args.append(capture_id)
        with self.connect() as conn:
            return [dict(row) for row in conn.execute(sql, args)]

    def _packet(self, row):
        data = dict(row)
        data["details"] = json.loads(data.pop("details_json"))
        return data

    @staticmethod
    def _size_bucket(length):
        if length < 128:
            return "<128 B"
        if length < 512:
            return "128-511 B"
        if length < 1024:
            return "512-1023 B"
        return ">=1024 B"

    @staticmethod
    def _duration_seconds(packets):
        if len(packets) < 2:
            return 0
        try:
            start = datetime.fromisoformat(str(packets[0]["timestamp"]).replace("Z", "+00:00"))
            end = datetime.fromisoformat(str(packets[-1]["timestamp"]).replace("Z", "+00:00"))
            return max((end - start).total_seconds(), 0)
        except ValueError:
            try:
                return max(float(packets[-1]["timestamp"]) - float(packets[0]["timestamp"]), 0)
            except (TypeError, ValueError):
                return max(len(packets) - 1, 0)
