"""Student-friendly financial product catalog and allocation policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProductOption:
    name: str
    category: str
    risk: int
    liquidity: str
    horizon: str
    role: str
    starter_tip: str


PRODUCT_OPTIONS: tuple[ProductOption, ...] = (
    ProductOption(
        name="余额宝 / 货币基金",
        category="现金管理",
        risk=1,
        liquidity="T+0/T+1",
        horizon="随取随用",
        role="生活费缓冲、短期备用金",
        starter_tip="先放 1-3 个月必要开销，再考虑更高波动资产。",
    ),
    ProductOption(
        name="银行活期+通知存款",
        category="现金管理",
        risk=1,
        liquidity="高",
        horizon="1天-7天",
        role="不用承担净值波动的现金停靠点",
        starter_tip="适合放学费、房租、考试报名费这类刚性支出。",
    ),
    ProductOption(
        name="短债基金",
        category="稳健增值",
        risk=2,
        liquidity="T+1/T+2",
        horizon="3个月以上",
        role="现金缓冲之外的低波动增值仓",
        starter_tip="会有净值波动，不适合放马上要用的钱。",
    ),
    ProductOption(
        name="中长期纯债基金",
        category="稳健增值",
        risk=3,
        liquidity="T+1/T+2",
        horizon="6个月以上",
        role="承担利率波动，换取相对稳定的收益来源",
        starter_tip="利率上行时可能回撤，别把它当保本产品。",
    ),
    ProductOption(
        name="沪深300 / 中证A500 指数基金",
        category="权益定投",
        risk=4,
        liquidity="T+1/T+2",
        horizon="3年以上",
        role="分享核心资产长期增长",
        starter_tip="用小额定投，不用生活费赌短期涨跌。",
    ),
    ProductOption(
        name="红利低波 ETF / 联接基金",
        category="权益定投",
        risk=4,
        liquidity="T+1/T+2",
        horizon="3年以上",
        role="偏防守型权益仓，适合搭配宽基",
        starter_tip="关注估值和行业集中度，不要只看股息率。",
    ),
    ProductOption(
        name="黄金 ETF / 联接基金",
        category="卫星配置",
        risk=4,
        liquidity="T+1/T+2",
        horizon="1年以上",
        role="对冲情绪和汇率波动的小比例资产",
        starter_tip="控制在小仓位，避免追涨。",
    ),
    ProductOption(
        name="可转债基金",
        category="进阶尝试",
        risk=5,
        liquidity="T+1/T+2",
        horizon="2年以上",
        role="股债混合波动来源",
        starter_tip="适合学习后少量体验，不适合作为第一只基金。",
    ),
    ProductOption(
        name="恒生科技 ETF / 联接基金",
        category="卫星配置",
        risk=5,
        liquidity="T+1/T+2",
        horizon="3年以上",
        role="港股科技龙头的地域分散仓",
        starter_tip="港股波动大，控制仓位，不追涨。",
    ),
)

RISK_LABELS = {
    1: "低风险",
    2: "中低风险",
    3: "中风险",
    4: "中高风险",
    5: "高风险",
}


def product_catalog() -> list[dict[str, Any]]:
    """Return product options as plain dictionaries."""
    return [
        {
            "name": item.name,
            "category": item.category,
            "risk": item.risk,
            "risk_label": RISK_LABELS[item.risk],
            "liquidity": item.liquidity,
            "horizon": item.horizon,
            "role": item.role,
            "starter_tip": item.starter_tip,
        }
        for item in PRODUCT_OPTIONS
    ]


def classify_risk_score(score: float) -> dict[str, Any]:
    """Map a 0-100 score to a student-friendly risk profile."""
    bounded = max(0.0, min(100.0, float(score)))
    if bounded < 35:
        return {
            "profile": "保守型",
            "summary": "优先守住现金流，权益仓只做很小比例体验。",
            "max_equity": 0.2,
        }
    if bounded < 70:
        return {
            "profile": "稳健型",
            "summary": "适合先建立备用金，再用小额定投建立长期仓位。",
            "max_equity": 0.4,
        }
    return {
        "profile": "成长型",
        "summary": "可承受一定波动，但仍要保留备用金和止损纪律。",
        "max_equity": 0.6,
    }


def build_student_allocation(
    monthly_income: float,
    monthly_expense: float,
    risk_score: float,
    *,
    reserve_months: int = 3,
) -> dict[str, Any]:
    """Create a simple allocation plan for a student's monthly surplus."""
    income = max(0.0, float(monthly_income))
    expense = max(0.0, float(monthly_expense))
    surplus = max(0.0, income - expense)
    profile = classify_risk_score(risk_score)

    emergency_target = expense * max(1, reserve_months)
    cash_ratio = 0.5 if surplus < 300 else 0.35
    stable_ratio = 0.25
    equity_ratio = min(profile["max_equity"], 1 - cash_ratio - stable_ratio)
    learning_ratio = max(0.0, 1 - cash_ratio - stable_ratio - equity_ratio)

    allocations = [
        {
            "bucket": "现金缓冲",
            "ratio": cash_ratio,
            "amount": round(surplus * cash_ratio, 2),
            "products": "余额宝、货币基金、银行活期+通知存款",
            "why": "先保证下月生活费和突发开支。",
        },
        {
            "bucket": "稳健增值",
            "ratio": stable_ratio,
            "amount": round(surplus * stable_ratio, 2),
            "products": "短债基金、纯债基金",
            "why": "让不用立刻花的钱承担较低波动。",
        },
        {
            "bucket": "长期定投",
            "ratio": equity_ratio,
            "amount": round(surplus * equity_ratio, 2),
            "products": "沪深300、中证A500、红利低波等指数基金",
            "why": "用小额、长期、分散的方式学习权益波动。",
        },
        {
            "bucket": "学习实验",
            "ratio": learning_ratio,
            "amount": round(surplus * learning_ratio, 2),
            "products": "黄金ETF、可转债基金等小仓位观察",
            "why": "把好奇心放进可承受的预算里。",
        },
    ]

    return {
        "monthly_income": income,
        "monthly_expense": expense,
        "monthly_surplus": round(surplus, 2),
        "emergency_target": round(emergency_target, 2),
        "profile": profile,
        "allocations": allocations,
        "guardrail": "不借钱投资，不用学费和下月生活费投资，不碰看不懂的产品。",
    }


def learning_prompts() -> list[dict[str, str]]:
    """Daily reflection prompts that teach investing process quality."""
    return [
        {
            "title": "先问钱的用途",
            "prompt": "这笔钱 3 个月内会不会用到？会用到就不要放进波动资产。",
        },
        {
            "title": "写下买入理由",
            "prompt": "如果不能用一句话说明为什么买，就先观察一周。",
        },
        {
            "title": "看最大回撤",
            "prompt": "想象账户短期下跌 20%，你会加仓、持有还是睡不着？",
        },
        {
            "title": "分清收益来源",
            "prompt": "货币基金靠流动性管理，债基吃利率和信用，权益基金吃企业盈利。",
        },
    ]
