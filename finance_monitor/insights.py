"""Derived insights and lightweight visual helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

BLOCKS = "▁▂▃▄▅▆▇█"


def _coerce_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def sparkline(values: Sequence[float]) -> str:
    """Render a tiny sparkline for terminal dashboards."""
    series = [_coerce_float(value) for value in values]
    series = [value for value in series if value is not None]
    if not series:
        return "-"
    if len(series) == 1:
        return BLOCKS[-1]

    low = min(series)
    high = max(series)
    if high == low:
        middle = BLOCKS[len(BLOCKS) // 2]
        return middle * len(series)

    scale = len(BLOCKS) - 1
    chars: list[str] = []
    for value in series:
        ratio = (value - low) / (high - low)
        index = int(round(ratio * scale))
        index = max(0, min(scale, index))
        chars.append(BLOCKS[index])
    return "".join(chars)


def _percent_change(first: float, last: float) -> float | None:
    if first == 0:
        return None
    return round(((last - first) / first) * 100, 2)


def _trend_label(change_pct: float | None) -> str:
    if change_pct is None:
        return "未知"
    if change_pct > 0.2:
        return "走强"
    if change_pct < -0.2:
        return "走弱"
    return "平稳"


def build_history_rows(
    history: Mapping[str, Sequence[Mapping[str, Any]]],
    index_names: Sequence[str],
    *,
    window: int = 7,
) -> list[dict[str, Any]]:
    """Summarize recent history into compact rows for the dashboard."""
    rows: list[dict[str, Any]] = []
    for name in index_names:
        raw_records = history.get(name, [])
        recent_records = [
            record
            for record in raw_records[-window:]
            if isinstance(record, Mapping)
        ]
        if not recent_records:
            continue

        close_series: list[float] = []
        pe_series: list[float] = []
        for record in recent_records:
            close = _coerce_float(record.get("close"))
            if close is not None:
                close_series.append(close)
            pe_percentile = _coerce_float(record.get("pe_percentile"))
            if pe_percentile is not None:
                pe_series.append(pe_percentile)

        if not close_series:
            continue

        latest = recent_records[-1]
        close_change_pct = _percent_change(close_series[0], close_series[-1])
        pe_delta = None
        if len(pe_series) >= 2:
            pe_delta = round(pe_series[-1] - pe_series[0], 2)
        latest_pe_percentile = _coerce_float(latest.get("pe_percentile"))

        rows.append(
            {
                "name": name,
                "date": str(latest.get("date", "-")),
                "close": round(close_series[-1], 4),
                "close_change_pct": close_change_pct,
                "pe_percentile": (
                    round(latest_pe_percentile, 1)
                    if latest_pe_percentile is not None
                    else None
                ),
                "pe_delta": pe_delta,
                "sparkline": sparkline(close_series),
                "trend": _trend_label(close_change_pct),
            }
        )
    return rows
