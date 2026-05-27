"""Market data fetch helpers."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import akshare as ak
import baostock as bs

try:  # pragma: no cover - import shim for direct script execution
    from .config import INDEX_LOOKBACK_DAYS
except ImportError:  # pragma: no cover
    from config import INDEX_LOOKBACK_DAYS


def bs_login():
    """Log in to BaoStock once per run."""
    result = bs.login()
    if result.error_code != "0":
        raise ConnectionError(f"BaoStock 登录失败: {result.error_msg}")
    return result


def bs_logout():
    """Log out of BaoStock if a session exists."""
    bs.logout()


def _to_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _pick_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def get_index_data(index_code: str) -> dict[str, Any] | None:
    """Fetch the latest daily close for a market index."""
    today = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=INDEX_LOOKBACK_DAYS)).strftime("%Y-%m-%d")

    rs = bs.query_history_k_data_plus(
        index_code,
        "date,close,preclose",
        start_date=start,
        end_date=today,
        frequency="d",
        adjustflag="3",
    )
    if rs.error_code != "0":
        print(f"  [baostock] {index_code} 查询失败: {rs.error_msg}")
        return None

    rows: list[list[str]] = []
    while rs.next():
        rows.append(rs.get_row_data())

    if not rows:
        return None

    latest = rows[-1]
    if len(latest) < 3:
        return None

    close = _to_float(latest[1])
    preclose = _to_float(latest[2])
    if close is None or preclose in (None, 0):
        return None

    return {
        "close": round(close, 4),
        "change_pct": round(((close - preclose) / preclose) * 100, 2),
        "date": latest[0],
    }


def get_fund_nav(fund_code: str) -> dict[str, Any] | None:
    """Fetch the latest open-end fund NAV."""
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        if df is None or df.empty:
            return None

        nav_column = _pick_column(list(df.columns), ("单位净值", "净值"))
        date_column = _pick_column(list(df.columns), ("净值日期", "日期"))
        if nav_column is None or date_column is None:
            return None

        latest = df.tail(2).reset_index(drop=True).iloc[-1]
        nav = _to_float(latest[nav_column])
        if nav is None:
            return None

        nav_prev = None
        if len(df) >= 2:
            prev_row = df.tail(2).reset_index(drop=True).iloc[-2]
            nav_prev = _to_float(prev_row[nav_column])

        return {
            "nav": round(nav, 4),
            "date": str(latest[date_column]),
            "nav_prev": nav_prev,
        }
    except Exception as exc:
        print(f"  [akshare] 基金 {fund_code} 净值获取失败: {exc}")
        return None


def get_index_valuation(lg_name: str) -> dict[str, Any] | None:
    """Fetch index valuation metrics from akshare."""
    try:
        df = ak.stock_index_pe_lg(symbol=lg_name)
        if df is None or df.empty:
            return None

        pe_column = _pick_column(
            list(df.columns),
            ("静态市盈率", "市盈率", "PE"),
        )
        percentile_column = _pick_column(
            list(df.columns),
            ("静态市盈率中位数", "市盈率中位数", "市盈率百分位", "PE百分位"),
        )
        if pe_column is None or percentile_column is None:
            return None

        latest = df.iloc[-1]
        pe = _to_float(latest[pe_column])
        pe_percentile = _to_float(latest[percentile_column])
        if pe is None or pe_percentile is None:
            return None

        return {
            "pe": round(pe, 2),
            "pe_percentile": round(pe_percentile, 1),
        }
    except Exception as exc:
        print(f"  [akshare] {lg_name} 估值获取失败: {exc}")
        return None


def get_hk_index_data() -> dict[str, Any] | None:
    """Fetch the latest Hang Seng Tech Index via akshare."""
    try:
        df = ak.stock_hk_index_daily_em(symbol="HSTECH")
        if df is None or df.empty:
            return None

        close_col = _pick_column(list(df.columns), ("收盘", "close", "收盘价"))
        date_col = _pick_column(list(df.columns), ("日期", "date", "时间"))
        if close_col is None or date_col is None:
            return None

        latest = df.iloc[-1]
        close = _to_float(latest[close_col])
        if close is None:
            return None

        change_pct = None
        if len(df) >= 2:
            prev_close = _to_float(df.iloc[-2][close_col])
            if prev_close and prev_close != 0:
                change_pct = round(((close - prev_close) / prev_close) * 100, 2)

        return {
            "close": round(close, 4),
            "change_pct": change_pct,
            "date": str(latest[date_col]),
        }
    except Exception as exc:
        print(f"  [akshare] 恒生科技指数获取失败: {exc}")
        return None
