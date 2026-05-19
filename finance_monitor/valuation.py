"""Valuation logic and monthly investment planning."""

from __future__ import annotations

from typing import Any

try:  # pragma: no cover - import shim for direct script execution
    from .config import (
        FUND_RATIO,
        HISTORY_FILE,
        MONTHLY_BUDGET,
        OVERVALUED_THRESHOLD,
        SAVINGS_RATIO,
        UNDERVALUED_THRESHOLD,
    )
    from .history import save_history as _save_history
except ImportError:  # pragma: no cover
    from config import (
        FUND_RATIO,
        HISTORY_FILE,
        MONTHLY_BUDGET,
        OVERVALUED_THRESHOLD,
        SAVINGS_RATIO,
        UNDERVALUED_THRESHOLD,
    )
    from history import save_history as _save_history


def judge_valuation(pe_percentile: float | None) -> dict[str, str]:
    """Judge market state from the PE percentile."""
    if pe_percentile is None:
        return {
            "level": "未知",
            "advice": "数据不足，暂时无法判断",
            "signal": "观望",
        }

    value = float(pe_percentile)
    if value < UNDERVALUED_THRESHOLD:
        return {
            "level": "低估",
            "advice": "市场处于历史低估区间，适合定投买入",
            "signal": "买入",
        }
    if value < OVERVALUED_THRESHOLD:
        return {
            "level": "合理",
            "advice": "市场估值合理，可继续定投或持有",
            "signal": "持有",
        }
    return {
        "level": "高估",
        "advice": "市场估值偏高，建议观望或分批止盈",
        "signal": "观望",
    }


def calculate_monthly_plan(avg_pe_percentile: float | None = None) -> dict[str, Any]:
    """Calculate the monthly investment split."""
    budget = float(MONTHLY_BUDGET)
    fund_amount = round(budget * FUND_RATIO, 2)
    savings_amount = round(budget * SAVINGS_RATIO, 2)

    plan = {
        "budget": budget,
        "fund_amount": fund_amount,
        "savings_amount": savings_amount,
    }

    if avg_pe_percentile is None:
        plan["action"] = "本月数据不足，按常规定投"
        plan["detail"] = (
            f"将 {fund_amount:.0f} 元投入指数基金，"
            f"{savings_amount:.0f} 元保留为现金缓冲"
        )
    elif avg_pe_percentile < UNDERVALUED_THRESHOLD:
        plan["action"] = "本月低估，建议全额定投"
        plan["detail"] = (
            f"将 {fund_amount:.0f} 元投入指数基金，"
            f"{savings_amount:.0f} 元继续放在余额宝"
        )
    elif avg_pe_percentile > OVERVALUED_THRESHOLD:
        plan["action"] = "本月高估，建议暂停定投"
        plan["detail"] = (
            f"将 {budget:.0f} 元全部放入余额宝，等待更好的入场时机"
        )
    else:
        plan["action"] = "本月估值合理，正常定投"
        plan["detail"] = (
            f"将 {fund_amount:.0f} 元投入指数基金，"
            f"{savings_amount:.0f} 元留作应急现金"
        )

    return plan


def save_history(
    index_name: str,
    pe_percentile: float,
    pe: float,
    close: float,
    *,
    history_file: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Compatibility wrapper around the history persistence layer."""
    target = HISTORY_FILE if history_file is None else history_file
    return _save_history(
        index_name,
        pe_percentile,
        pe,
        close,
        history_file=target,
    )
