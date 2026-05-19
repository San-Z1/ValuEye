"""Terminal rendering helpers built on top of rich."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def _signal_style(signal: str) -> str:
    return {"买入": "green", "持有": "yellow", "观望": "red"}.get(signal, "white")


def _format_pct(value: float | None) -> str:
    if value is None:
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def _format_points(value: float | None) -> str:
    if value is None:
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f} pts"


def print_header():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    console.print()
    console.rule(f"[bold cyan]ValuEye 终端晨报 - {now}[/]")
    console.print()


def print_index_table(indices_data: list[dict[str, Any]]):
    table = Table(title="核心指数行情", show_header=True, header_style="bold cyan")
    table.add_column("指数", style="bold", min_width=10)
    table.add_column("最新价", justify="right")
    table.add_column("涨跌幅", justify="right")
    table.add_column("日期", justify="center")

    for item in indices_data:
        if not item:
            continue
        change = item.get("change_pct")
        change_style = "green" if (change or 0) >= 0 else "red"
        sign = "+" if (change or 0) >= 0 else ""
        table.add_row(
            str(item.get("name", "-")),
            f"{float(item.get('close', 0.0)):.2f}",
            f"[{change_style}]{sign}{float(change or 0.0):.2f}%[/]",
            str(item.get("date", "-")),
        )

    console.print(table)
    console.print()


def print_valuation_table(valuations: list[dict[str, Any]]):
    table = Table(title="指数估值分析", show_header=True, header_style="bold cyan")
    table.add_column("指数", style="bold", min_width=10)
    table.add_column("PE", justify="right")
    table.add_column("PE分位", justify="right")
    table.add_column("层级", justify="center")
    table.add_column("建议", justify="center")

    for item in valuations:
        if not item:
            continue
        color = _signal_style(str(item.get("signal", "观望")))
        table.add_row(
            str(item.get("name", "-")),
            f"{float(item.get('pe', 0.0)):.2f}",
            f"[{color}]{float(item.get('pe_percentile', 0.0)):.1f}%[/]",
            f"[{color}]{item.get('level', '-')}[/]",
            f"[{color}]{item.get('signal', '-')}[/]",
        )

    console.print(table)
    console.print()


def print_fund_table(funds_data: list[dict[str, Any]]):
    table = Table(title="基金净值", show_header=True, header_style="bold cyan")
    table.add_column("基金名称", style="bold", min_width=20)
    table.add_column("代码", justify="center")
    table.add_column("最新净值", justify="right")
    table.add_column("日变化", justify="right")
    table.add_column("日期", justify="center")

    for item in funds_data:
        if not item:
            continue
        nav = float(item.get("nav", 0.0))
        nav_prev = item.get("nav_prev")
        if nav_prev is not None:
            change = ((nav - float(nav_prev)) / float(nav_prev)) * 100 if nav_prev else None
            change_style = "green" if (change or 0) >= 0 else "red"
            change_text = f"[{change_style}]{_format_pct(change)}[/]"
        else:
            change_text = "-"

        table.add_row(
            str(item.get("name", "-")),
            str(item.get("code", "-")),
            f"{nav:.4f}",
            change_text,
            str(item.get("date", "-")),
        )

    console.print(table)
    console.print()


def print_history_table(history_rows: list[dict[str, Any]]):
    if not history_rows:
        return

    table = Table(title="近7日历史趋势", show_header=True, header_style="bold cyan")
    table.add_column("指数", style="bold", min_width=10)
    table.add_column("7日走势", justify="left")
    table.add_column("收盘变化", justify="right")
    table.add_column("PE分位变化", justify="right")
    table.add_column("最新日期", justify="center")

    for item in history_rows:
        close_change = item.get("close_change_pct")
        close_style = "green" if (close_change or 0) >= 0 else "red"
        pe_delta = item.get("pe_delta")
        pe_style = "green" if pe_delta is not None and pe_delta <= 0 else "red"
        table.add_row(
            str(item.get("name", "-")),
            str(item.get("sparkline", "-")),
            f"[{close_style}]{_format_pct(close_change)}[/]",
            f"[{pe_style}]{_format_points(pe_delta)}[/]",
            str(item.get("date", "-")),
        )

    console.print(table)
    console.print()


def print_investment_plan(plan: dict[str, Any]):
    text = Text()
    text.append("本月预算: ", style="bold")
    text.append(f"{float(plan.get('budget', 0.0)):.0f} 元\n")
    text.append("指数定投: ", style="bold")
    text.append(f"{float(plan.get('fund_amount', 0.0)):.0f} 元\n")
    text.append("现金缓冲: ", style="bold")
    text.append(f"{float(plan.get('savings_amount', 0.0)):.0f} 元\n\n")
    text.append("操作建议: ", style="bold cyan")
    text.append(f"{plan.get('action', '-')}\n")
    text.append(str(plan.get("detail", "-")))

    console.print(Panel(text, title="本月投资计划", border_style="cyan"))
    console.print()


def print_overall_advice(avg_percentile: float | None, signal: str, advice: str):
    color = _signal_style(signal)
    text = Text()
    text.append("整体 PE 分位: ", style="bold")
    text.append("-" if avg_percentile is None else f"{avg_percentile:.1f}%")
    text.append("\n市场状态: ", style="bold")
    text.append(f"{advice}\n\n")
    text.append("建议: ", style="bold")
    if avg_percentile is None:
        text.append("先按常规定投，等数据恢复后再细化判断", style="bold yellow")
    elif signal == "买入":
        text.append("按计划执行本月定投", style="bold green")
    elif signal == "观望":
        text.append("先保留现金，再观察入场时机", style="bold red")
    else:
        text.append("保持纪律，继续常规定投", style="bold yellow")

    console.print(Panel(text, title="综合操作建议", border_style=color))
    console.print()


def print_footer():
    console.print("[dim]投资有风险，以上内容仅供学习参考，不构成投资建议。[/]")
    console.print("[dim]长期定投重于短期波动，先守住现金流，再谈收益。[/]")
    console.rule()
