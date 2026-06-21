from fastapi import APIRouter, Query
from typing import List, Optional

from app.services.stats_service import StatsService
from app.schemas.session import (
    DailySessionCount,
    DailyTokenUsage,
    ModelDistribution,
    HourlyDistribution,
    StatsSummary,
)

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
async def get_summary():
    return await StatsService.get_summary()


@router.get("/daily-sessions", response_model=List[DailySessionCount])
async def get_daily_sessions(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    return await StatsService.get_daily_session_count(days=days)


@router.get("/daily-tokens", response_model=List[DailyTokenUsage])
async def get_daily_tokens(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    return await StatsService.get_daily_token_usage(days=days)


@router.get("/model-distribution", response_model=List[ModelDistribution])
async def get_model_distribution(
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter by days")
):
    return await StatsService.get_model_distribution(days=days)


@router.get("/hourly-distribution", response_model=List[HourlyDistribution])
async def get_hourly_distribution(
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter by days")
):
    return await StatsService.get_hourly_distribution(days=days)
