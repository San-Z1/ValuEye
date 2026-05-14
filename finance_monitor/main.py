#!/usr/bin/env python3
"""ValuEye - 大学生理财监控"""

import sys
import os
import locale

# Windows 终端中文编码修复
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        os.system("chcp 65001 >nul 2>&1")

# 将当前目录加入 path，确保能找到同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import INDICES, FUNDS
from data_fetcher import get_index_data, get_fund_nav, get_index_valuation
from valuation import judge_valuation, calculate_monthly_plan, save_history
from display import (
    console,
    print_header,
    print_index_table,
    print_valuation_table,
    print_fund_table,
    print_investment_plan,
    print_overall_advice,
    print_footer,
)


def fetch_all_index_data() -> list:
    """抓取所有指数行情"""
    results = []
    for idx in INDICES:
        console.print(f"  抓取 [cyan]{idx['name']}[/] 行情...", end=" ")
        data = get_index_data(idx["code"])
        if data:
            data["name"] = idx["name"]
            results.append(data)
            console.print("[green]OK[/]")
        else:
            console.print("[red]失败[/]")
    return results


def fetch_all_valuations() -> list:
    """抓取所有指数估值"""
    results = []
    for idx in INDICES:
        console.print(f"  抓取 [cyan]{idx['name']}[/] 估值...", end=" ")
        val = get_index_valuation(idx["lg_name"])
        if val:
            val["name"] = idx["name"]
            val.update(judge_valuation(val["pe_percentile"]))
            results.append(val)
            console.print("[green]OK[/]")
        else:
            console.print("[yellow]无数据（部分指数可能不支持）[/]")
    return results


def fetch_all_fund_nav() -> list:
    """抓取所有基金净值"""
    results = []
    for fund in FUNDS:
        console.print(f"  抓取 [cyan]{fund['name']}[/] 净值...", end=" ")
        data = get_fund_nav(fund["code"])
        if data:
            data["name"] = fund["name"]
            data["code"] = fund["code"]
            results.append(data)
            console.print("[green]OK[/]")
        else:
            console.print("[red]失败[/]")
    return results


def main():
    print_header()

    # 1. 抓取指数行情
    console.print("[bold]1. 获取指数行情[/]")
    indices_data = fetch_all_index_data()
    if indices_data:
        print_index_table(indices_data)
    else:
        console.print("[red]所有指数数据获取失败，请检查网络连接[/]\n")

    # 2. 抓取估值数据
    console.print("[bold]2. 获取估值数据[/]")
    valuations = fetch_all_valuations()
    if valuations:
        print_valuation_table(valuations)
    else:
        console.print("[yellow]估值数据获取失败，将使用默认建议[/]\n")

    # 3. 抓取基金净值
    console.print("[bold]3. 获取基金净值[/]")
    funds_data = fetch_all_fund_nav()
    if funds_data:
        print_fund_table(funds_data)
    else:
        console.print("[yellow]基金净值获取失败[/]\n")

    # 4. 综合分析
    console.print("[bold]4. 综合分析[/]")
    avg_pe_percentile = None
    overall_signal = "持有"
    overall_advice_text = "数据不足，建议按计划定投"

    if valuations:
        valid = [v for v in valuations if v.get("pe_percentile") is not None]
        if valid:
            avg_pe_percentile = sum(v["pe_percentile"] for v in valid) / len(valid)
            overall = judge_valuation(avg_pe_percentile)
            overall_signal = overall["signal"]
            overall_advice_text = overall["advice"]

    # 投资计划
    plan = calculate_monthly_plan(avg_pe_percentile)
    print_investment_plan(plan)

    # 综合建议
    if avg_pe_percentile is not None:
        print_overall_advice(avg_pe_percentile, overall_signal, overall_advice_text)

    # 5. 保存历史
    if indices_data and valuations:
        console.print("[bold]5. 保存历史数据[/]")
        val_map = {v["name"]: v for v in valuations}
        for idx in indices_data:
            if idx["name"] in val_map:
                v = val_map[idx["name"]]
                save_history(
                    idx["name"],
                    v["pe_percentile"],
                    v["pe"],
                    idx["close"],
                )
                console.print(f"  已保存 [cyan]{idx['name']}[/] 数据")
        console.print()

    print_footer()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]程序出错: {e}[/]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
