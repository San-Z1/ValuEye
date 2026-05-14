"""估值分析与投资建议模块"""

import json
import os
from datetime import datetime
from config import (
    UNDERVALUED_THRESHOLD,
    OVERVALUED_THRESHOLD,
    MONTHLY_BUDGET,
    FUND_RATIO,
    SAVINGS_RATIO,
    HISTORY_FILE,
)


def judge_valuation(pe_percentile: float) -> dict:
    """根据 PE 百分位判断市场状态

    Returns:
        {"level": "低估"/"合理"/"高估", "advice": 建议文字, "signal": 买入/持有/观望}
    """
    if pe_percentile is None:
        return {"level": "未知", "advice": "数据不足，无法判断", "signal": "观望"}

    if pe_percentile < UNDERVALUED_THRESHOLD:
        return {
            "level": "低估",
            "advice": "市场处于历史低估区间，适合定投买入",
            "signal": "买入",
        }
    elif pe_percentile < OVERVALUED_THRESHOLD:
        return {
            "level": "合理",
            "advice": "市场估值合理，可继续定投或持有",
            "signal": "持有",
        }
    else:
        return {
            "level": "高估",
            "advice": "市场估值偏高，建议观望或分批止盈",
            "signal": "观望",
        }


def calculate_monthly_plan(avg_pe_percentile: float = None) -> dict:
    """计算每月投资分配方案

    Returns:
        包含预算分配和操作建议的字典
    """
    fund_amount = MONTHLY_BUDGET * FUND_RATIO
    savings_amount = MONTHLY_BUDGET * SAVINGS_RATIO

    plan = {
        "budget": MONTHLY_BUDGET,
        "fund_amount": fund_amount,
        "savings_amount": savings_amount,
    }

    if avg_pe_percentile is not None and avg_pe_percentile < UNDERVALUED_THRESHOLD:
        plan["action"] = "本月低估，建议全额定投"
        plan["detail"] = f"将 {fund_amount:.0f} 元投入指数基金，{savings_amount:.0f} 元存余额宝"
    elif avg_pe_percentile is not None and avg_pe_percentile > OVERVALUED_THRESHOLD:
        plan["action"] = "本月高估，建议暂停定投"
        plan["detail"] = f"将 {MONTHLY_BUDGET:.0f} 元全部转入余额宝，等待更好时机"
    else:
        plan["action"] = "本月估值合理，正常定投"
        plan["detail"] = f"将 {fund_amount:.0f} 元投入指数基金，{savings_amount:.0f} 元存余额宝"

    return plan


def save_history(index_name: str, pe_percentile: float, pe: float, close: float):
    """保存历史数据到 JSON 文件"""
    history = {}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = {}

    today = datetime.now().strftime("%Y-%m-%d")
    if index_name not in history:
        history[index_name] = []

    history[index_name].append({
        "date": today,
        "pe": pe,
        "pe_percentile": pe_percentile,
        "close": close,
    })

    # 只保留最近 365 条记录
    history[index_name] = history[index_name][-365:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
