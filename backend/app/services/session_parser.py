import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid


class SessionParser:
    @staticmethod
    def parse_file(file_path: Path) -> Optional[Dict]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            file_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

            data = json.loads(content)

            parser = SessionParser._detect_parser(data)
            if parser:
                parsed = parser(data, file_path.name)
                parsed["file_hash"] = file_hash
                parsed["source_file"] = file_path.name
                return parsed

            return None
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    @staticmethod
    def _detect_parser(data: Dict):
        if "messages" in data and isinstance(data["messages"], list):
            if all(
                isinstance(m, dict) and ("role" in m or "sender" in m)
                for m in data["messages"]
            ):
                return SessionParser._parse_standard_format

        if "conversation" in data and isinstance(data["conversation"], dict):
            return SessionParser._parse_conversation_format

        if "chat_messages" in data or "chat_history" in data:
            return SessionParser._parse_chat_history_format

        if "uuid" in data or "name" in data:
            return SessionParser._parse_claude_desktop_format

        return None

    @staticmethod
    def _parse_standard_format(data: Dict, filename: str) -> Dict:
        messages_data = data.get("messages", [])
        session_id = data.get("id", data.get("uuid", str(uuid.uuid4())))
        title = data.get("title", data.get("name", ""))

        if not title:
            title = SessionParser._extract_title(messages_data)

        created_at = data.get("created_at", data.get("timestamp", 0))
        if isinstance(created_at, str):
            created_at = SessionParser._parse_timestamp(created_at)

        updated_at = data.get("updated_at", data.get("last_message_time", created_at))
        if isinstance(updated_at, str):
            updated_at = SessionParser._parse_timestamp(updated_at)

        messages = []
        total_input_tokens = 0
        total_output_tokens = 0
        model = data.get("model", "")

        for idx, msg in enumerate(messages_data):
            role = msg.get("role", msg.get("sender", "user"))
            content = msg.get("content", "")

            if isinstance(content, list):
                content_parts = []
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        content_parts.append(part["text"])
                    elif isinstance(part, str):
                        content_parts.append(part)
                content = "\n".join(content_parts)

            msg_model = msg.get("model", model)
            msg_created_at = msg.get("created_at", msg.get("timestamp", created_at))
            if isinstance(msg_created_at, str):
                msg_created_at = SessionParser._parse_timestamp(msg_created_at)

            input_tokens = msg.get("input_tokens", msg.get("prompt_tokens", 0)) or 0
            output_tokens = msg.get("output_tokens", msg.get("completion_tokens", 0)) or 0

            if role == "assistant":
                total_output_tokens += output_tokens
            else:
                total_input_tokens += input_tokens

            msg_id = msg.get("id", f"{session_id}_msg_{idx}")

            messages.append(
                {
                    "id": str(msg_id),
                    "session_id": str(session_id),
                    "role": role,
                    "content": str(content),
                    "model": msg_model,
                    "created_at": float(msg_created_at) if msg_created_at else 0.0,
                    "tokens": input_tokens + output_tokens,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "message_index": idx,
                }
            )

        if messages:
            if created_at == 0:
                created_at = messages[0]["created_at"]
            if updated_at == 0:
                updated_at = messages[-1]["created_at"]

        return {
            "id": str(session_id),
            "title": title,
            "created_at": float(created_at),
            "updated_at": float(updated_at),
            "model": model,
            "total_tokens": total_input_tokens + total_output_tokens,
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "message_count": len(messages),
            "messages": messages,
            "raw_data": json.dumps(data, ensure_ascii=False),
        }

    @staticmethod
    def _parse_conversation_format(data: Dict, filename: str) -> Dict:
        conv = data.get("conversation", {})
        messages_data = conv.get("messages", [])
        return SessionParser._parse_standard_format(
            {**data, "messages": messages_data}, filename
        )

    @staticmethod
    def _parse_chat_history_format(data: Dict, filename: str) -> Dict:
        messages_data = data.get("chat_messages", data.get("chat_history", []))
        return SessionParser._parse_standard_format(
            {**data, "messages": messages_data}, filename
        )

    @staticmethod
    def _parse_claude_desktop_format(data: Dict, filename: str) -> Dict:
        messages_data = data.get("chat_messages", [])
        if not messages_data and "messages" in data:
            messages_data = data["messages"]

        session_id = data.get("uuid", data.get("id", str(uuid.uuid4())))
        title = data.get("name", data.get("title", ""))

        if not title:
            title = SessionParser._extract_title(messages_data)

        created_at = data.get("created_at", data.get("timestamp", 0))
        if isinstance(created_at, str):
            created_at = SessionParser._parse_timestamp(created_at)

        updated_at = data.get("updated_at", data.get("last_edited_time", created_at))
        if isinstance(updated_at, str):
            updated_at = SessionParser._parse_timestamp(updated_at)

        return SessionParser._parse_standard_format(
            {
                "id": session_id,
                "title": title,
                "created_at": created_at,
                "updated_at": updated_at,
                "model": data.get("model", ""),
                "messages": messages_data,
            },
            filename,
        )

    @staticmethod
    def _extract_title(messages: List[Dict]) -> str:
        if not messages:
            return "Untitled"

        first_msg = messages[0]
        content = first_msg.get("content", "")

        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and "text" in part:
                    content = part["text"]
                    break
            else:
                content = ""

        if isinstance(content, str):
            lines = content.strip().split("\n")
            first_line = lines[0] if lines else ""
            title = first_line[:50].strip()
            return title if title else "Untitled"

        return "Untitled"

    @staticmethod
    def _parse_timestamp(ts: str) -> float:
        if not ts:
            return 0.0

        try:
            if ts.endswith("Z"):
                ts = ts.replace("Z", "+00:00")

            dt = datetime.fromisoformat(ts)
            return dt.timestamp()
        except (ValueError, TypeError):
            try:
                return float(ts)
            except (ValueError, TypeError):
                return 0.0
