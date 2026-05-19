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
]

FUNDS = [
    {"name": "天弘沪深300ETF联接A", "code": "000961"},
    {"name": "天弘中证500ETF联接A", "code": "000962"},
    {"name": "华夏上证50ETF联接A", "code": "001051"},
]

UNDERVALUED_THRESHOLD = 30.0
OVERVALUED_THRESHOLD = 70.0

MONTHLY_BUDGET = 200.0
FUND_RATIO = 0.8
SAVINGS_RATIO = 0.2

TREND_WINDOW = 7
HISTORY_LIMIT = 365
INDEX_LOOKBACK_DAYS = 10

HISTORY_FILE = BASE_DIR / "history.json"
