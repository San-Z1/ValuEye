"""Offline demo data for classroom and static-dashboard previews."""

from __future__ import annotations

from datetime import datetime
from typing import Any

try:  # pragma: no cover
    from .json_export import SCHEMA_VERSION, validate_dashboard_payload
except ImportError:  # pragma: no cover
    from json_export import SCHEMA_VERSION, validate_dashboard_payload


DEMO_INDICES: tuple[dict[str, Any], ...] = (
    {
        "name": "沪深300",
        "close": 3914.60,
        "change_pct": 1.23,
        "date": "2026-06-08",
        "pe": 14.17,
        "pe_percentile": 22.0,
        "level": "低估",
        "signal": "买入",
    },
    {
        "name": "中证500",
        "close": 5670.16,
        "change_pct": -0.87,
        "date": "2026-06-08",
        "pe": 32.42,
        "pe_percentile": 33.2,
        "level": "合理",
        "signal": "持有",
    },
    {
        "name": "上证50",
        "close": 2996.57,
        "change_pct": 0.45,
        "date": "2026-06-08",
        "pe": 11.46,
        "pe_percentile": 18.1,
        "level": "低估",
        "signal": "买入",
    },
    {
        "name": "创业板指",
        "close": 2156.00,
        "change_pct": 0.56,
        "date": "2026-06-08",
        "pe": 35.20,
        "pe_percentile": 15.0,
        "level": "低估",
        "signal": "买入",
    },
    {
        "name": "中证1000",
        "close": 6234.00,
        "change_pct": -1.02,
        "date": "2026-06-08",
        "pe": 42.10,
        "pe_percentile": 45.0,
        "level": "合理",
        "signal": "持有",
    },
    {
        "name": "中证红利",
        "close": 5812.00,
        "change_pct": 0.18,
        "date": "2026-06-08",
        "pe": 7.80,
        "pe_percentile": 38.0,
        "level": "合理",
        "signal": "持有",
    },
    {
        "name": "恒生科技",
        "close": 4521.00,
        "change_pct": 2.10,
        "date": "2026-06-08",
        "pe": None,
        "pe_percentile": None,
        "level": "无数据",
        "signal": "观望",
    },
)

DEMO_FUNDS: tuple[dict[str, Any], ...] = (
    {
        "name": "天弘沪深300ETF联接A",
        "code": "000961",
        "nav": 1.7387,
        "change_pct": 1.23,
        "date": "2026-06-08",
        "category": "宽基核心",
    },
    {
        "name": "天弘中证500ETF联接A",
        "code": "000962",
        "nav": 1.6939,
        "change_pct": -0.87,
        "date": "2026-06-08",
        "category": "宽基中盘",
    },
    {
        "name": "华安黄金ETF联接A",
        "code": "000216",
        "nav": 5.8720,
        "change_pct": 0.12,
        "date": "2026-06-08",
        "category": "黄金对冲",
    },
    {
        "name": "天弘中证红利ETF联接A",
        "code": "013794",
        "nav": 1.2341,
        "change_pct": 0.18,
        "date": "2026-06-08",
        "category": "红利防守",
    },
    {
        "name": "华夏恒生科技ETF联接A",
        "code": "013402",
        "nav": 0.8912,
        "change_pct": 2.10,
        "date": "2026-06-08",
        "category": "港股卫星",
    },
)


def build_demo_dashboard_data(
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a schema-compatible dashboard payload without live API calls."""
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now().isoformat(timespec="seconds"),
        "indices": [dict(item) for item in DEMO_INDICES],
        "funds": [dict(item) for item in DEMO_FUNDS],
        "recommendation": {
            "risk_profile": "稳健型",
            "signal": "买入",
            "advice": "示例数据处于偏低估区域，适合用小额定投练习纪律。",
            "avg_pe_percentile": 24.4,
            "monthly_budget": 200.0,
            "allocations": [
                {"fund": "天弘沪深300ETF联接A", "code": "000961", "ratio": 0.40, "amount": 80.0},
                {"fund": "天弘中证500ETF联接A", "code": "000962", "ratio": 0.20, "amount": 40.0},
                {"fund": "华安黄金ETF联接A", "code": "000216", "ratio": 0.15, "amount": 30.0},
                {"fund": "天弘中证红利ETF联接A", "code": "013794", "ratio": 0.15, "amount": 30.0},
                {"fund": "华夏恒生科技ETF联接A", "code": "013402", "ratio": 0.10, "amount": 20.0},
            ],
        },
        "market_summary": {
            "avg_pe_percentile": 24.4,
            "overall_signal": "买入",
            "overall_advice": "示例市场处于历史偏低估区间，适合演示定投买入流程。",
        },
    }
    validate_dashboard_payload(payload)
    return payload
