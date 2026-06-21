from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.services.session_service import SessionService
from app.schemas.session import (
    Session,
    SessionDetail,
    Message,
    ScanResult,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=dict)
async def list_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query("", description="Search by title"),
    model: str = Query("", description="Filter by model"),
    sort_by: str = Query("updated_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order"),
):
    sessions, total = await SessionService.get_sessions(
        page=page,
        page_size=page_size,
        search=search,
        model=model,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {
        "items": sessions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/models", response_model=List[str])
async def get_models():
    return await SessionService.get_available_models()


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    session = await SessionService.get_session_detail(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/{session_id}/messages", response_model=List[Message])
async def get_messages(session_id: str):
    messages = await SessionService.get_session_messages(session_id)
    if not messages:
        session = await SessionService.get_session_detail(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    return messages


@router.get("/{session_id}/raw")
async def get_raw_session(session_id: str):
    raw = await SessionService.get_raw_session(session_id)
    if not raw:
        raise HTTPException(status_code=404, detail="Session not found")
    return raw


@router.post("/scan", response_model=ScanResult)
async def scan_sessions(sessions_dir: Optional[str] = None):
    result = await SessionService.scan_sessions(sessions_dir)
    return result


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    deleted = await SessionService.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}
