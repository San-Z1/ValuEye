#!/usr/bin/env python3
"""PennyPilot main entrypoint."""

from __future__ import annotations

import os
import sys
import traceback
from typing import Any

if sys.platform == "win32":  # pragma: no cover - convenience for console encoding
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        os.system("chcp 65001 >nul 2>&1")

try:  # pragma: no cover - import shim for direct script execution
    from .catalog import build_student_allocation, learning_prompts, product_catalog
    from .config import FUNDS, INDICES, OVERVALUED_THRESHOLD, STUDENT_PROFILE, TREND_WINDOW, UNDERVALUED_THRESHOLD
    from .data_fetcher import (
        bs_login,
        bs_logout,
        get_fund_nav,
        get_hk_index_data,
        get_index_data,
        get_index_valuation,
    )
    from .display import (
        console,
        print_footer,
        print_fund_table,
        print_header,
        print_history_table,
        print_index_table,
        print_investment_plan,
        print_learning_prompts,
        print_overall_advice,
        print_product_catalog,
        print_student_allocation,
        print_valuation_table,
    )
    from .demo_data import build_demo_dashboard_data
    from .history import load_history
    from .insights import build_history_rows
    from .json_export import DATA_FILE, export_to_json, validate_dashboard_payload
    from .valuation import calculate_monthly_plan, judge_valuation, save_history
except ImportError:  # pragma: no cover
    from catalog import build_student_allocation, learning_prompts, product_catalog
    from config import FUNDS, INDICES, OVERVALUED_THRESHOLD, STUDENT_PROFILE, TREND_WINDOW, UNDERVALUED_THRESHOLD
    from data_fetcher import (
        bs_login,
        bs_logout,
        get_fund_nav,
        get_hk_index_data,
        get_index_data,
        get_index_valuation,
    )
    from display import (
        console,
        print_footer,
        print_fund_table,
        print_header,
        print_history_table,
        print_index_table,
        print_investment_plan,
        print_learning_prompts,
        print_overall_advice,
        print_product_catalog,
        print_student_allocation,
        print_valuation_table,
    )
    from demo_data import build_demo_dashboard_data
    from history import load_history
    from insights import build_history_rows
    from json_export import DATA_FILE, export_to_json, validate_dashboard_payload
    from valuation import calculate_monthly_plan, judge_valuation, save_history


def _write_dashboard_payload(payload: dict[str, Any]) -> None:
    validate_dashboard_payload(payload)
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as handle:
        import json

        json.dump(payload, handle, ensure_ascii=False, indent=2)


def _run_demo_data_export() -> None:
    payload = build_demo_dashboard_data()
    _write_dashboard_payload(payload)
    console.print(f"[green]已生成离线演示数据:[/] [cyan]{DATA_FILE}[/]")


def _fetch_all_index_data() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in INDICES:
        console.print(f"  获取 [cyan]{item['name']}[/] 行情...", end=" ")
        if item["code"].startswith("hk:"):
            data = get_hk_index_data()
        else:
            data = get_index_data(item["code"])
        if data:
            data["name"] = item["name"]
            results.append(data)
            console.print("[green]OK[/]")
        else:
            console.print("[red]失败[/]")
    return results


def _fetch_all_valuations() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in INDICES:
        if item["lg_name"] is None:
            console.print(f"  [cyan]{item['name']}[/] 估值... [dim]跳过（无PE数据）[/]")
            continue
        console.print(f"  获取 [cyan]{item['name']}[/] 估值...", end=" ")
        valuation = get_index_valuation(item["lg_name"])
        if valuation:
            valuation["name"] = item["name"]
            valuation.update(judge_valuation(valuation["pe_percentile"]))
            results.append(valuation)
            console.print("[green]OK[/]")
        else:
            console.print("[yellow]无数据[/]")
    return results


def _fetch_all_fund_nav() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in FUNDS:
        console.print(f"  获取 [cyan]{item['name']}[/] 净值...", end=" ")
        data = get_fund_nav(item["code"])
        if data:
            data["name"] = item["name"]
            data["code"] = item["code"]
            results.append(data)
            console.print("[green]OK[/]")
        else:
            console.print("[red]失败[/]")
    return results


def _summarize_market(valuations: list[dict[str, Any]]) -> tuple[float | None, str, str, str]:
    valid = [item for item in valuations if item.get("pe_percentile") is not None]
    if not valid:
        return None, "持有", "数据不足，建议按常规定投", "稳健型"

    avg_pe_percentile = sum(float(item["pe_percentile"]) for item in valid) / len(valid)
    overall = judge_valuation(avg_pe_percentile)
    if avg_pe_percentile < UNDERVALUED_THRESHOLD:
        risk_label = "成长型"
    elif avg_pe_percentile > OVERVALUED_THRESHOLD:
        risk_label = "保守型"
    else:
        risk_label = "稳健型"
    return avg_pe_percentile, overall["signal"], overall["advice"], risk_label


def _save_snapshot(indices_data: list[dict[str, Any]], valuations: list[dict[str, Any]]):
    if not indices_data or not valuations:
        return

    console.print("[bold]5. 保存历史数据[/]")
    valuation_map = {item["name"]: item for item in valuations}
    for index_item in indices_data:
        valuation_item = valuation_map.get(index_item["name"])
        if not valuation_item:
            continue
        save_history(
            index_item["name"],
            valuation_item["pe_percentile"],
            valuation_item["pe"],
            index_item["close"],
        )
        console.print(f"  已保存 [cyan]{index_item['name']}[/] 的最新数据")
    console.print()


def _render_history_trend():
    history = load_history()
    history_rows = build_history_rows(
        history,
        [item["name"] for item in INDICES],
        window=TREND_WINDOW,
    )
    print_history_table(history_rows)


def _render_learning_layer():
    allocation = build_student_allocation(
        STUDENT_PROFILE["monthly_income"],
        STUDENT_PROFILE["monthly_expense"],
        STUDENT_PROFILE["risk_score"],
        reserve_months=int(STUDENT_PROFILE["cash_reserve_months"]),
    )
    print_student_allocation(allocation)
    print_product_catalog(product_catalog())
    print_learning_prompts(learning_prompts())


def _run() -> None:
    console.print("[bold]1. 获取指数行情[/]")
    indices_data = _fetch_all_index_data()
    if indices_data:
        print_index_table(indices_data)
    else:
        console.print("[red]指数行情暂时不可用，请检查网络或 BaoStock 状态。[/]\n")

    console.print("[bold]2. 获取估值数据[/]")
    valuations = _fetch_all_valuations()
    if valuations:
        print_valuation_table(valuations)
    else:
        console.print("[yellow]估值数据暂时不可用，将按保守方案继续。[/]\n")

    console.print("[bold]3. 获取基金净值[/]")
    funds_data = _fetch_all_fund_nav()
    if funds_data:
        print_fund_table(funds_data)
    else:
        console.print("[yellow]基金净值暂时不可用。[/]\n")

    console.print("[bold]4. 综合分析[/]")
    avg_pe_percentile, overall_signal, overall_advice, risk_profile = _summarize_market(valuations)
    plan = calculate_monthly_plan(avg_pe_percentile)
    print_investment_plan(plan)
    print_overall_advice(avg_pe_percentile, overall_signal, overall_advice)

    _save_snapshot(indices_data, valuations)
    _render_history_trend()
    console.print("[bold]6. 理财思维训练[/]")
    _render_learning_layer()
    console.print("[bold]7. 生成前端数据[/]")
    try:
        json_path = export_to_json(
            indices_data, valuations, funds_data,
            risk_profile, overall_signal, overall_advice,
            avg_pe_percentile,
        )
        console.print(f"  已生成 [cyan]{json_path}[/]\n")
    except Exception as exc:
        console.print(f"  [yellow]JSON 导出失败: {exc}[/]\n")
    print_footer()


def main() -> int:
    print_header()
    if "--demo-data" in sys.argv:
        try:
            _run_demo_data_export()
            print_footer()
            return 0
        except Exception as exc:
            console.print(f"\n[red]离线演示数据生成失败: {exc}[/]")
            traceback.print_exc()
            return 1

    logged_in = False
    try:
        try:
            bs_login()
            logged_in = True
        except Exception as exc:
            console.print(f"[yellow]BaoStock 登录失败，继续使用可用数据: {exc}[/]")

        _run()
        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断[/]")
        return 130
    except Exception as exc:
        console.print(f"\n[red]程序出错: {exc}[/]")
        traceback.print_exc()
        return 1
    finally:
        if logged_in:
            bs_logout()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
