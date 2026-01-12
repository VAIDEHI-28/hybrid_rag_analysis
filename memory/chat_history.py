import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("storage/chat_history.db")


class ChatHistory:
    def __init__(self):
        DB_PATH.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            session_id TEXT,
            role TEXT,
            message TEXT,
            timestamp TEXT
        )
        """)
        self.conn.commit()

    def add_message(self, session_id: str, role: str, message: str):
        self.conn.execute(
            "INSERT INTO chat_history VALUES (?, ?, ?, ?)",
            (session_id, role, message, datetime.utcnow().isoformat())
        )
        self.conn.commit()

    def get_history(self, session_id: str):
        cursor = self.conn.execute(
            "SELECT role, message FROM chat_history WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )
        return cursor.fetchall()
