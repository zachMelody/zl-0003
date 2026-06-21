from typing import List, Optional
from datetime import datetime, timedelta

from app.database import db
from app.schemas.session import (
    DailySessionCount,
    DailyTokenUsage,
    ModelDistribution,
    HourlyDistribution,
    StatsSummary,
)


class StatsService:
    @staticmethod
    async def get_daily_session_count(days: int = 30) -> List[DailySessionCount]:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        start_ts = datetime.combine(start_date, datetime.min.time()).timestamp()
        end_ts = datetime.combine(end_date, datetime.max.time()).timestamp()

        sql = """
            SELECT 
                date(created_at, 'unixepoch', 'localtime') as date,
                COUNT(*) as count
            FROM sessions
            WHERE created_at >= ? AND created_at <= ?
            GROUP BY date(created_at, 'unixepoch', 'localtime')
            ORDER BY date ASC
        """
        rows = await db.fetchall(sql, (start_ts, end_ts))

        result_dict = {row["date"]: row["count"] for row in rows}

        results = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            date_str = d.strftime("%Y-%m-%d")
            results.append(
                DailySessionCount(
                    date=date_str,
                    count=result_dict.get(date_str, 0),
                )
            )

        return results

    @staticmethod
    async def get_daily_token_usage(days: int = 30) -> List[DailyTokenUsage]:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        start_ts = datetime.combine(start_date, datetime.min.time()).timestamp()
        end_ts = datetime.combine(end_date, datetime.max.time()).timestamp()

        sql = """
            SELECT 
                date(created_at, 'unixepoch', 'localtime') as date,
                SUM(input_tokens) as input_tokens,
                SUM(output_tokens) as output_tokens,
                SUM(total_tokens) as total_tokens
            FROM sessions
            WHERE created_at >= ? AND created_at <= ?
            GROUP BY date(created_at, 'unixepoch', 'localtime')
            ORDER BY date ASC
        """
        rows = await db.fetchall(sql, (start_ts, end_ts))

        result_dict = {}
        for row in rows:
            result_dict[row["date"]] = {
                "input_tokens": row["input_tokens"] or 0,
                "output_tokens": row["output_tokens"] or 0,
                "total_tokens": row["total_tokens"] or 0,
            }

        results = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            date_str = d.strftime("%Y-%m-%d")
            data = result_dict.get(
                date_str,
                {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            )
            results.append(
                DailyTokenUsage(
                    date=date_str,
                    input_tokens=data["input_tokens"],
                    output_tokens=data["output_tokens"],
                    total_tokens=data["total_tokens"],
                )
            )

        return results

    @staticmethod
    async def get_model_distribution(days: Optional[int] = None) -> List[ModelDistribution]:
        where_sql = ""
        params = []

        if days:
            start_ts = (datetime.now() - timedelta(days=days)).timestamp()
            where_sql = "WHERE created_at >= ?"
            params = [start_ts]

        sql = f"""
            SELECT 
                COALESCE(NULLIF(model, ''), 'unknown') as model,
                COUNT(*) as count,
                SUM(total_tokens) as total_tokens
            FROM sessions
            {where_sql}
            GROUP BY model
            ORDER BY count DESC
        """
        rows = await db.fetchall(sql, tuple(params))

        return [
            ModelDistribution(
                model=row["model"],
                count=row["count"],
                total_tokens=row["total_tokens"] or 0,
            )
            for row in rows
        ]

    @staticmethod
    async def get_hourly_distribution(days: Optional[int] = None) -> List[HourlyDistribution]:
        where_sql = ""
        params = []

        if days:
            start_ts = (datetime.now() - timedelta(days=days)).timestamp()
            where_sql = "WHERE created_at >= ?"
            params = [start_ts]

        sql = f"""
            SELECT 
                CAST(strftime('%H', created_at, 'unixepoch', 'localtime') as INTEGER) as hour,
                COUNT(*) as count
            FROM sessions
            {where_sql}
            GROUP BY hour
            ORDER BY hour ASC
        """
        rows = await db.fetchall(sql, tuple(params))

        result_dict = {row["hour"]: row["count"] for row in rows}

        results = []
        for hour in range(24):
            results.append(
                HourlyDistribution(
                    hour=hour,
                    count=result_dict.get(hour, 0),
                )
            )

        return results

    @staticmethod
    async def get_summary() -> StatsSummary:
        sql_total = """
            SELECT 
                COUNT(*) as total_sessions,
                SUM(message_count) as total_messages,
                SUM(total_tokens) as total_tokens,
                SUM(input_tokens) as total_input_tokens,
                SUM(output_tokens) as total_output_tokens,
                MIN(created_at) as min_created_at,
                MAX(created_at) as max_created_at
            FROM sessions
        """
        row = await db.fetchone(sql_total)

        if not row or row["total_sessions"] == 0:
            return StatsSummary(
                total_sessions=0,
                total_messages=0,
                total_tokens=0,
                total_input_tokens=0,
                total_output_tokens=0,
            )

        date_start = None
        date_end = None
        if row["min_created_at"]:
            date_start = datetime.fromtimestamp(row["min_created_at"]).strftime(
                "%Y-%m-%d"
            )
        if row["max_created_at"]:
            date_end = datetime.fromtimestamp(row["max_created_at"]).strftime(
                "%Y-%m-%d"
            )

        return StatsSummary(
            total_sessions=row["total_sessions"] or 0,
            total_messages=row["total_messages"] or 0,
            total_tokens=row["total_tokens"] or 0,
            total_input_tokens=row["total_input_tokens"] or 0,
            total_output_tokens=row["total_output_tokens"] or 0,
            date_range_start=date_start,
            date_range_end=date_end,
        )
