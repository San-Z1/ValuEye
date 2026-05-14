"""终端美化输出模块 - 使用 rich 库"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime


console = Console()


def _color_by_signal(signal: str) -> str:
    """根据操作信号返回颜色"""
    return {"买入": "green", "持有": "yellow", "观望": "red"}.get(signal, "white")


def _emoji_by_signal(signal: str) -> str:
    """根据操作信号返回 emoji"""
    return {"买入": "[bold green]买入[/]", "持有": "[bold yellow]持有[/]", "观望": "[bold red]观望[/]"}.get(signal, "未知")


def print_header():
    """打印报告头部"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    console.print()
    console.rule(f"[bold cyan]PennyPilot 理财晨报 - {now}[/]")
    console.print()


def print_index_table(indices_data: list):
    """打印指数行情表格

    Args:
        indices_data: [{"name": "沪深300", "close": 3985.23, "change_pct": 1.25, "date": "2026-05-14"}, ...]
    """
    table = Table(title="PennyPilot 核心指数行情", show_header=True, header_style="bold cyan")
    table.add_column("指数", style="bold", min_width=10)
    table.add_column("最新价", justify="right")
    table.add_column("涨跌幅", justify="right")
    table.add_column("日期", justify="center")

    for item in indices_data:
        if item is None:
            continue
        pct = item["change_pct"]
        pct_color = "green" if pct >= 0 else "red"
        pct_sign = "+" if pct >= 0 else ""
        table.add_row(
            item["name"],
            f"{item['close']:.2f}",
            f"[{pct_color}]{pct_sign}{pct:.2f}%[/]",
            item["date"],
        )

    console.print(table)
    console.print()


def print_valuation_table(valuations: list):
    """打印估值分析表格

    Args:
        valuations: [{"name": "沪深300", "pe": 12.5, "pe_percentile": 35.0, "signal": "持有", "advice": "..."}, ...]
    """
    table = Table(title="指数估值分析", show_header=True, header_style="bold cyan")
    table.add_column("指数", style="bold", min_width=10)
    table.add_column("PE", justify="right")
    table.add_column("PE百分位", justify="right")
    table.add_column("估值水平", justify="center")
    table.add_column("操作建议", justify="center")

    for item in valuations:
        if item is None:
            continue
        color = _color_by_signal(item["signal"])
        table.add_row(
            item["name"],
            f"{item['pe']:.2f}",
            f"[{color}]{item['pe_percentile']:.1f}%[/]",
            f"[{color}]{item['level']}[/]",
            _emoji_by_signal(item["signal"]),
        )

    console.print(table)
    console.print()


def print_fund_table(funds_data: list):
    """打印基金净值表格

    Args:
        funds_data: [{"name": "...", "code": "...", "nav": 1.234, "date": "...", "nav_prev": 1.230}, ...]
    """
    table = Table(title="基金净值", show_header=True, header_style="bold cyan")
    table.add_column("基金名称", style="bold", min_width=20)
    table.add_column("代码", justify="center")
    table.add_column("最新净值", justify="right")
    table.add_column("日涨跌", justify="right")
    table.add_column("日期", justify="center")

    for item in funds_data:
        if item is None:
            continue
        nav = item["nav"]
        nav_prev = item.get("nav_prev")
        if nav_prev:
            change = ((nav - nav_prev) / nav_prev) * 100
            change_color = "green" if change >= 0 else "red"
            change_str = f"[{change_color}]{'+' if change >= 0 else ''}{change:.2f}%[/]"
        else:
            change_str = "-"

        table.add_row(
            item["name"],
            item["code"],
            f"{nav:.4f}",
            change_str,
            item.get("date", "-"),
        )

    console.print(table)
    console.print()


def print_investment_plan(plan: dict):
    """打印每月投资计划面板"""
    text = Text()
    text.append(f"每月预算: ", style="bold")
    text.append(f"{plan['budget']:.0f} 元\n")
    text.append(f"基金定投: ", style="bold")
    text.append(f"{plan['fund_amount']:.0f} 元\n")
    text.append(f"余额宝:   ", style="bold")
    text.append(f"{plan['savings_amount']:.0f} 元\n\n")
    text.append(f"操作建议: ", style="bold cyan")
    text.append(f"{plan['action']}\n")
    text.append(f"{plan['detail']}")

    console.print(Panel(text, title="本月投资计划", border_style="cyan"))
    console.print()


def print_overall_advice(avg_percentile: float, signal: str, advice: str):
    """打印综合建议面板"""
    color = _color_by_signal(signal)

    text = Text()
    text.append(f"整体 PE 百分位: ", style="bold")
    text.append(f"{avg_percentile:.1f}%\n")
    text.append(f"市场状态: ", style="bold")
    text.append(f"{advice}\n\n")

    if signal == "买入":
        text.append("建议执行本月定投计划", style="bold green")
    elif signal == "观望":
        text.append("建议暂停定投，资金转入余额宝", style="bold red")
    else:
        text.append("正常定投，保持纪律", style="bold yellow")

    console.print(Panel(text, title="综合操作建议", border_style=color))
    console.print()


def print_footer():
    """打印报告尾部"""
    console.print("[dim]投资有风险，以上仅供参考，不构成投资建议[/]")
    console.print("[dim]坚持定投纪律，长期持有，不追涨杀跌[/]")
    console.rule()
