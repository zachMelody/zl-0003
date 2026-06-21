import json
import time
from typing import List, Optional, Dict, Tuple
from pathlib import Path

from app.database import db
from app.schemas.session import (
    Session,
    SessionDetail,
    Message,
    ScanResult,
)
from app.services.session_parser import SessionParser
from app.config import settings


class SessionService:
    @staticmethod
    def _row_to_session(row) -> Session:
        session = Session(
            id=row["id"],
            title=row["title"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            model=row["model"] or "",
            total_tokens=row["total_tokens"] or 0,
            input_tokens=row["input_tokens"] or 0,
            output_tokens=row["output_tokens"] or 0,
            message_count=row["message_count"] or 0,
            source_file=row["source_file"],
        )
        from datetime import datetime
        session.created_at_str = datetime.fromtimestamp(session.created_at).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        session.updated_at_str = datetime.fromtimestamp(session.updated_at).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return session

    @staticmethod
    def _row_to_message(row) -> Message:
        msg = Message(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            model=row["model"] or "",
            created_at=row["created_at"],
            tokens=row["tokens"] or 0,
            input_tokens=row["input_tokens"] or 0,
            output_tokens=row["output_tokens"] or 0,
            message_index=row["message_index"],
        )
        from datetime import datetime
        msg.created_at_str = datetime.fromtimestamp(msg.created_at).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return msg

    @staticmethod
    async def get_sessions(
        page: int = 1,
        page_size: int = 20,
        search: str = "",
        model: str = "",
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Session], int]:
        offset = (page - 1) * page_size

        where_clauses = []
        params = []

        if search:
            where_clauses.append("title LIKE ?")
            params.append(f"%{search}%")

        if model:
            where_clauses.append("model = ?")
            params.append(model)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        order_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
        order_column = sort_by if sort_by in ["created_at", "updated_at", "title", "total_tokens", "message_count"] else "updated_at"

        count_sql = f"SELECT COUNT(*) as count FROM sessions {where_sql}"
        count_row = await db.fetchone(count_sql, tuple(params))
        total = count_row["count"] if count_row else 0

        sql = f"""
            SELECT * FROM sessions
            {where_sql}
            ORDER BY {order_column} {order_direction}
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        rows = await db.fetchall(sql, tuple(params))

        sessions = [SessionService._row_to_session(row) for row in rows]
        return sessions, total

    @staticmethod
    async def get_session_detail(session_id: str) -> Optional[SessionDetail]:
        sql = "SELECT * FROM sessions WHERE id = ?"
        row = await db.fetchone(sql, (session_id,))

        if not row:
            return None

        session = SessionService._row_to_session(row)
        session_detail = SessionDetail(**session.model_dump())

        msg_sql = """
            SELECT * FROM messages
            WHERE session_id = ?
            ORDER BY message_index ASC
        """
        msg_rows = await db.fetchall(msg_sql, (session_id,))
        session_detail.messages = [
            SessionService._row_to_message(r) for r in msg_rows
        ]

        return session_detail

    @staticmethod
    async def get_session_messages(session_id: str) -> List[Message]:
        sql = """
            SELECT * FROM messages
            WHERE session_id = ?
            ORDER BY message_index ASC
        """
        rows = await db.fetchall(sql, (session_id,))
        return [SessionService._row_to_message(row) for row in rows]

    @staticmethod
    async def get_available_models() -> List[str]:
        sql = "SELECT DISTINCT model FROM sessions WHERE model != '' ORDER BY model"
        rows = await db.fetchall(sql)
        return [row["model"] for row in rows]

    @staticmethod
    async def scan_sessions(sessions_dir: Optional[str] = None) -> ScanResult:
        dir_path = Path(sessions_dir) if sessions_dir else settings.sessions_full_dir
        dir_path.mkdir(parents=True, exist_ok=True)

        json_files = list(dir_path.rglob("*.json")) + list(dir_path.rglob("*.jsonl"))
        
        total_files = len(json_files)
        new_sessions = 0
        updated_sessions = 0
        skipped_sessions = 0

        for file_path in json_files:
            parsed = SessionParser.parse_file(file_path)
            if not parsed:
                skipped_sessions += 1
                continue

            session_id = parsed["id"]
            file_hash = parsed["file_hash"]

            existing = await db.fetchone(
                "SELECT file_hash FROM sessions WHERE id = ?",
                (session_id,),
            )

            if existing:
                if existing["file_hash"] == file_hash:
                    skipped_sessions += 1
                    continue
                else:
                    await SessionService._update_session(parsed)
                    updated_sessions += 1
            else:
                await SessionService._insert_session(parsed)
                new_sessions += 1

        return ScanResult(
            total_files=total_files,
            new_sessions=new_sessions,
            updated_sessions=updated_sessions,
            skipped_sessions=skipped_sessions,
        )

    @staticmethod
    async def _insert_session(parsed: Dict):
        now = time.time()
        await db.execute(
            """
            INSERT INTO sessions (
                id, title, created_at, updated_at, model,
                total_tokens, input_tokens, output_tokens, message_count,
                source_file, file_hash, raw_data, scanned_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                parsed["id"],
                parsed["title"],
                parsed["created_at"],
                parsed["updated_at"],
                parsed["model"],
                parsed["total_tokens"],
                parsed["input_tokens"],
                parsed["output_tokens"],
                parsed["message_count"],
                parsed["source_file"],
                parsed["file_hash"],
                parsed["raw_data"],
                now,
            ),
        )

        for msg in parsed["messages"]:
            await db.execute(
                """
                INSERT INTO messages (
                    id, session_id, role, content, model,
                    created_at, tokens, input_tokens, output_tokens, message_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    msg["id"],
                    msg["session_id"],
                    msg["role"],
                    msg["content"],
                    msg["model"],
                    msg["created_at"],
                    msg["tokens"],
                    msg["input_tokens"],
                    msg["output_tokens"],
                    msg["message_index"],
                ),
            )

    @staticmethod
    async def _update_session(parsed: Dict):
        await db.execute(
            "DELETE FROM messages WHERE session_id = ?",
            (parsed["id"],),
        )

        now = time.time()
        await db.execute(
            """
            UPDATE sessions SET
                title = ?, created_at = ?, updated_at = ?, model = ?,
                total_tokens = ?, input_tokens = ?, output_tokens = ?,
                message_count = ?, source_file = ?, file_hash = ?,
                raw_data = ?, scanned_at = ?
            WHERE id = ?
            """,
            (
                parsed["title"],
                parsed["created_at"],
                parsed["updated_at"],
                parsed["model"],
                parsed["total_tokens"],
                parsed["input_tokens"],
                parsed["output_tokens"],
                parsed["message_count"],
                parsed["source_file"],
                parsed["file_hash"],
                parsed["raw_data"],
                now,
                parsed["id"],
            ),
        )

        for msg in parsed["messages"]:
            await db.execute(
                """
                INSERT INTO messages (
                    id, session_id, role, content, model,
                    created_at, tokens, input_tokens, output_tokens, message_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    msg["id"],
                    msg["session_id"],
                    msg["role"],
                    msg["content"],
                    msg["model"],
                    msg["created_at"],
                    msg["tokens"],
                    msg["input_tokens"],
                    msg["output_tokens"],
                    msg["message_index"],
                ),
            )

    @staticmethod
    async def delete_session(session_id: str) -> bool:
        await db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        result = await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        return result.rowcount > 0

    @staticmethod
    async def get_raw_session(session_id: str) -> Optional[Dict]:
        row = await db.fetchone(
            "SELECT raw_data FROM sessions WHERE id = ?", (session_id,)
        )
        if row:
            return json.loads(row["raw_data"])
        return None
