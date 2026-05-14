"""数据抓取模块 - BaoStock 获取指数行情 + akshare 获取基金净值和估值"""

import baostock as bs
import akshare as ak
from datetime import datetime, timedelta


def bs_login():
    """BaoStock 登录（程序启动时调用一次）"""
    lg = bs.login()
    if lg.error_code != "0":
        raise ConnectionError(f"BaoStock 登录失败: {lg.error_msg}")
    return lg


def bs_logout():
    """BaoStock 登出（程序退出时调用一次）"""
    bs.logout()


def get_index_data(index_code: str) -> dict:
    """用 BaoStock 获取指数最新行情

    Args:
        index_code: BaoStock 格式，如 "sh.000300"

    Returns:
        {"close": 收盘价, "change_pct": 涨跌幅%, "date": 日期}

    注意：调用前需先调用 bs_login()
    """
    today = datetime.now().strftime("%Y-%m-%d")
    # 往前多取几天，确保非交易日也能拿到数据
    start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

    rs = bs.query_history_k_data_plus(
        index_code,
        "date,close,preclose",
        start_date=start,
        end_date=today,
        frequency="d",
        adjustflag="3",
    )

    rows = []
    while rs.error_code == "0" and rs.next():
        rows.append(rs.get_row_data())

    if not rows:
        return None

    # 取最后一个交易日
    latest = rows[-1]
    date, close_str, preclose_str = latest[0], latest[1], latest[2]

    if not close_str or not preclose_str:
        return None

    try:
        close = float(close_str)
        preclose = float(preclose_str)
    except (ValueError, TypeError):
        return None
    change_pct = ((close - preclose) / preclose) * 100 if preclose else 0

    return {
        "close": close,
        "change_pct": round(change_pct, 2),
        "date": date,
    }


def get_fund_nav(fund_code: str) -> dict:
    """用 akshare 获取基金最新净值

    Args:
        fund_code: 基金代码，如 "000961"

    Returns:
        {"nav": 最新净值, "date": 日期, "nav_prev": 前一日净值}
    """
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        if df is None or df.empty:
            return None

        # 取最后两行
        df = df.tail(2).reset_index(drop=True)
        latest = df.iloc[-1]

        nav = float(latest["单位净值"])
        date_str = str(latest["净值日期"])

        nav_prev = None
        if len(df) >= 2:
            nav_prev = float(df.iloc[-2]["单位净值"])

        return {"nav": nav, "date": date_str, "nav_prev": nav_prev}
    except Exception as e:
        print(f"  [akshare] 获取基金 {fund_code} 净值失败: {e}")
        return None


def get_index_valuation(lg_name: str) -> dict:
    """用 akshare 获取指数估值（PE 及历史百分位）

    数据源：乐咕乐股 (legulegu) 通过 akshare 的 stock_index_pe_lg 接口
    支持的指数：沪深300、中证500、上证50、中证1000 等

    Args:
        lg_name: 乐咕乐股指数名称，如 "沪深300"

    Returns:
        {"pe": 静态市盈率, "pe_percentile": 静态市盈率中位数(%)}
    """
    try:
        df = ak.stock_index_pe_lg(symbol=lg_name)
        if df is None or df.empty:
            return None

        latest = df.iloc[-1]
        try:
            pe = float(latest["静态市盈率"])
            pe_percentile = float(latest["静态市盈率中位数"])
        except (ValueError, TypeError):
            return None

        return {
            "pe": round(pe, 2),
            "pe_percentile": round(pe_percentile, 1),
        }
    except Exception as e:
        print(f"  [akshare] 获取 {lg_name} 估值失败: {e}")
        return None
