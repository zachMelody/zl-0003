from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageBase(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    model: Optional[str] = ""
    created_at: float
    tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    message_index: int


class Message(MessageBase):
    created_at_str: Optional[str] = None

    class Config:
        from_attributes = True


class SessionBase(BaseModel):
    id: str
    title: str
    created_at: float
    updated_at: float
    model: Optional[str] = ""
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    message_count: int = 0
    source_file: str


class Session(SessionBase):
    created_at_str: Optional[str] = None
    updated_at_str: Optional[str] = None

    class Config:
        from_attributes = True


class SessionDetail(Session):
    messages: List[Message] = []


class DailySessionCount(BaseModel):
    date: str
    count: int


class DailyTokenUsage(BaseModel):
    date: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class ModelDistribution(BaseModel):
    model: str
    count: int
    total_tokens: int


class HourlyDistribution(BaseModel):
    hour: int
    count: int


class ScanResult(BaseModel):
    total_files: int
    new_sessions: int
    updated_sessions: int
    skipped_sessions: int


class StatsSummary(BaseModel):
    total_sessions: int
    total_messages: int
    total_tokens: int
    total_input_tokens: int
    total_output_tokens: int
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
