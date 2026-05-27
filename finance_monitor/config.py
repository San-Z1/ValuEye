"""Central configuration for the PennyPilot monitor."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

APP_NAME = "ValuEye"
APP_TAGLINE = "Student-friendly market monitor"

INDICES = [
    {"name": "沪深300", "code": "sh.000300", "lg_name": "沪深300"},
    {"name": "中证500", "code": "sh.000905", "lg_name": "中证500"},
    {"name": "上证50", "code": "sh.000016", "lg_name": "上证50"},
    {"name": "创业板指", "code": "sz.399006", "lg_name": "创业板指"},
    {"name": "中证1000", "code": "sh.000852", "lg_name": "中证1000"},
    {"name": "中证红利", "code": "sh.000922", "lg_name": "中证红利"},
    {"name": "恒生科技", "code": "hk:HSTECH", "lg_name": None},
]

FUNDS = [
    {"name": "天弘沪深300ETF联接A", "code": "000961", "category": "宽基核心"},
    {"name": "天弘中证500ETF联接A", "code": "000962", "category": "宽基中盘"},
    {"name": "华安黄金ETF联接A", "code": "000216", "category": "黄金对冲"},
    {"name": "天弘中证红利ETF联接A", "code": "013794", "category": "红利防守"},
    {"name": "华夏恒生科技ETF联接A", "code": "013402", "category": "港股卫星"},
]

UNDERVALUED_THRESHOLD = 30.0
OVERVALUED_THRESHOLD = 70.0

MONTHLY_BUDGET = 200.0
FUND_RATIO = 0.8
SAVINGS_RATIO = 0.2

STUDENT_PROFILE = {
    "monthly_income": 1200.0,
    "monthly_expense": 900.0,
    "cash_reserve_months": 3,
    "risk_score": 45,
}

TREND_WINDOW = 7
HISTORY_LIMIT = 365
INDEX_LOOKBACK_DAYS = 10

HISTORY_FILE = BASE_DIR / "history.json"

DCA_PRESETS = {
    "保守型": [
        {"code": "000961", "name": "天弘沪深300ETF联接A", "ratio": 0.40},
        {"code": "000216", "name": "华安黄金ETF联接A", "ratio": 0.35},
        {"code": "013794", "name": "天弘中证红利ETF联接A", "ratio": 0.15},
        {"code": "000962", "name": "天弘中证500ETF联接A", "ratio": 0.10},
    ],
    "稳健型": [
        {"code": "000961", "name": "天弘沪深300ETF联接A", "ratio": 0.40},
        {"code": "000962", "name": "天弘中证500ETF联接A", "ratio": 0.20},
        {"code": "000216", "name": "华安黄金ETF联接A", "ratio": 0.15},
        {"code": "013794", "name": "天弘中证红利ETF联接A", "ratio": 0.15},
        {"code": "013402", "name": "华夏恒生科技ETF联接A", "ratio": 0.10},
    ],
    "成长型": [
        {"code": "000961", "name": "天弘沪深300ETF联接A", "ratio": 0.30},
        {"code": "000962", "name": "天弘中证500ETF联接A", "ratio": 0.25},
        {"code": "013794", "name": "天弘中证红利ETF联接A", "ratio": 0.15},
        {"code": "013402", "name": "华夏恒生科技ETF联接A", "ratio": 0.15},
        {"code": "000216", "name": "华安黄金ETF联接A", "ratio": 0.15},
    ],
}

ASSET_CATEGORIES = {
    "000961": "宽基核心",
    "000962": "宽基中盘",
    "000216": "黄金对冲",
    "013794": "红利防守",
    "013402": "港股卫星",
}
