"""配置中心 - 指数、基金、估值阈值"""

import os

# 脚本所在目录，用于生成绝对路径
_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== 监控的指数 =====
# BaoStock 指数代码格式：sh.000300 / sz.399006
# legulegu 名称需与 BaoStock 代码对应
INDICES = [
    {"name": "沪深300", "code": "sh.000300", "lg_name": "沪深300"},
    {"name": "中证500", "code": "sh.000905", "lg_name": "中证500"},
    {"name": "上证50", "code": "sh.000016", "lg_name": "上证50"},
]

# ===== 监控的基金（场外基金，适合定投） =====
FUNDS = [
    {"name": "天弘沪深300ETF联接A", "code": "000961"},
    {"name": "天弘中证500ETF联接A", "code": "000962"},
    {"name": "华夏上证50ETF联接A", "code": "001051"},
]

# ===== 估值阈值（PE 百分位） =====
# 低于此值 = 低估，建议加仓
UNDERVALUED_THRESHOLD = 30
# 高于此值 = 高估，建议观望/止盈
OVERVALUED_THRESHOLD = 70

# ===== 每月预算 =====
MONTHLY_BUDGET = 200.0
# 投资比例：80% 投基金，20% 存余额宝
FUND_RATIO = 0.8
SAVINGS_RATIO = 0.2

# ===== 数据存储 =====
HISTORY_FILE = os.path.join(_DIR, "history.json")
