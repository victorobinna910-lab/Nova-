import sqlite3
from datetime import datetime
from pathlib import Path

from nova.config import MEMORY_DB_PATH

DB_PATH = Path(__file__).resolve().parent.parent / MEMORY_DB_PATH
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class NovaMemory:
    """Nova's long-term memory."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def remember(self, key: str, value: str) -> None:
        now = datetime.now().isoformat()
        self.conn.execute(
            """
            INSERT INTO memories (key, value, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (key, value, now, now),
        )
        self.conn.commit()

    def recall(self, key: str) -> str | None:
        row = self.conn.execute(
            "SELECT value FROM memories WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def search(self, query: str) -> list[tuple[str, str]]:
        rows = self.conn.execute(
            "SELECT key, value FROM memories WHERE key LIKE ? OR value LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        return rows

    def forget(self, key: str) -> bool:
        cursor = self.conn.execute("DELETE FROM memories WHERE key = ?", (key,))
        self.conn.commit()
        return cursor.rowcount > 0

    def all_memories(self) -> list[tuple[str, str]]:
        return self.conn.execute("SELECT key, value FROM memories").fetchall()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
