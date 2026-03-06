from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(slots=True)
class SessionRecord:
    user_id: int
    started_at: str
    duration_seconds: float
    target_text: str
    typed_text: str
    gross_wpm: float
    net_wpm: float
    accuracy: float
    uncorrected_errors: int
    backspace_count: int
    micro_stats: list[dict]


class TypingRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;

                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    started_at TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    target_text TEXT NOT NULL,
                    typed_text TEXT NOT NULL,
                    gross_wpm REAL NOT NULL,
                    net_wpm REAL NOT NULL,
                    accuracy REAL NOT NULL,
                    uncorrected_errors INTEGER NOT NULL,
                    backspace_count INTEGER NOT NULL,
                    micro_stats_json TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """
            )

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register(self, username: str, password: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        pwd_hash = self._hash_password(password)
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO users(username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, pwd_hash, now),
            )
            return int(cursor.lastrowid)

    def login(self, username: str, password: str) -> int | None:
        pwd_hash = self._hash_password(password)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if not row:
                return None
            if row["password_hash"] != pwd_hash:
                return None
            return int(row["id"])

    def save_session(self, record: SessionRecord) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO sessions (
                    user_id, started_at, duration_seconds, target_text, typed_text,
                    gross_wpm, net_wpm, accuracy, uncorrected_errors,
                    backspace_count, micro_stats_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.user_id,
                    record.started_at,
                    record.duration_seconds,
                    record.target_text,
                    record.typed_text,
                    record.gross_wpm,
                    record.net_wpm,
                    record.accuracy,
                    record.uncorrected_errors,
                    record.backspace_count,
                    json.dumps(record.micro_stats),
                ),
            )
            return int(cursor.lastrowid)

    def load_user_sessions(self, user_id: int) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, user_id, started_at, duration_seconds, target_text, typed_text,
                       gross_wpm, net_wpm, accuracy, uncorrected_errors,
                       backspace_count, micro_stats_json
                FROM sessions
                WHERE user_id = ?
                ORDER BY id
                """,
                (user_id,),
            ).fetchall()

        sessions: list[dict] = []
        for row in rows:
            session = dict(row)
            session["micro_stats"] = json.loads(session.pop("micro_stats_json"))
            sessions.append(session)
        return sessions
