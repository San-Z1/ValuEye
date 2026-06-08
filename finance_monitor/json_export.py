"""Export market data to web/data.json for the frontend dashboard."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from .catalog import product_catalog
    from .config import ASSET_CATEGORIES, BASE_DIR, DCA_PRESETS, MONTHLY_BUDGET
except ImportError:  # pragma: no cover
    from catalog import product_catalog
    from config import ASSET_CATEGORIES, BASE_DIR, DCA_PRESETS, MONTHLY_BUDGET

WEB_DIR = BASE_DIR.parent / "web"
DATA_FILE = WEB_DIR / "data.json"
SCHEMA_VERSION = 1


def _build_indices(
    indices_data: list[dict[str, Any]],
    valuations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    valuation_map = {item["name"]: item for item in valuations}
    result = []
    for idx in indices_data:
        v = valuation_map.get(idx["name"], {})
        result.append({
            "name": idx["name"],
            "close": idx.get("close"),
            "change_pct": idx.get("change_pct"),
            "date": idx.get("date"),
            "pe": v.get("pe"),
            "pe_percentile": v.get("pe_percentile"),
            "level": v.get("level", "无数据"),
            "signal": v.get("signal", "观望"),
        })
    return result


def _build_funds(funds_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for fund in funds_data:
        nav = fund.get("nav")
        nav_prev = fund.get("nav_prev")
        change_pct = None
        if nav is not None and nav_prev and nav_prev != 0:
            change_pct = round(((nav - nav_prev) / nav_prev) * 100, 2)
        result.append({
            "name": fund["name"],
            "code": fund.get("code", ""),
            "nav": nav,
            "change_pct": change_pct,
            "date": fund.get("date"),
            "category": ASSET_CATEGORIES.get(fund.get("code", ""), ""),
        })
    return result


def _build_recommendation(
    risk_profile: str,
    signal: str,
    advice: str,
    avg_pe_percentile: float | None,
) -> dict[str, Any]:
    preset = DCA_PRESETS.get(risk_profile, DCA_PRESETS["稳健型"])
    budget = float(MONTHLY_BUDGET)
    allocations = [
        {
            "fund": item["name"],
            "code": item["code"],
            "ratio": item["ratio"],
            "amount": round(budget * item["ratio"], 2),
        }
        for item in preset
    ]
    return {
        "risk_profile": risk_profile,
        "signal": signal,
        "advice": advice,
        "avg_pe_percentile": avg_pe_percentile,
        "monthly_budget": budget,
        "allocations": allocations,
    }


def validate_dashboard_payload(payload: dict[str, Any]) -> None:
    """Validate the dashboard JSON contract before writing it to disk."""
    required_top_level = {
        "schema_version",
        "generated_at",
        "indices",
        "funds",
        "recommendation",
        "market_summary",
        "products",
    }
    missing = required_top_level - set(payload)
    if missing:
        raise ValueError(f"dashboard payload missing fields: {sorted(missing)}")

    if payload["schema_version"] != SCHEMA_VERSION:
        raise ValueError("dashboard payload has unsupported schema_version")

    if not isinstance(payload["indices"], list):
        raise TypeError("dashboard payload indices must be a list")
    if not isinstance(payload["funds"], list):
        raise TypeError("dashboard payload funds must be a list")
    if not isinstance(payload["recommendation"], dict):
        raise TypeError("dashboard payload recommendation must be an object")
    if not isinstance(payload["products"], list):
        raise TypeError("dashboard payload products must be a list")

    for index, item in enumerate(payload["indices"]):
        for field in ("name", "level", "signal"):
            if field not in item:
                raise ValueError(f"indices[{index}] missing {field}")

    recommendation = payload["recommendation"]
    for field in ("risk_profile", "signal", "advice", "monthly_budget", "allocations"):
        if field not in recommendation:
            raise ValueError(f"recommendation missing {field}")
    if not isinstance(recommendation["allocations"], list):
        raise TypeError("recommendation allocations must be a list")

    for index, item in enumerate(payload["products"]):
        for field in ("name", "category", "risk", "risk_label", "liquidity", "horizon", "role", "starter_tip"):
            if field not in item:
                raise ValueError(f"products[{index}] missing {field}")


def export_to_json(
    indices_data: list[dict[str, Any]],
    valuations: list[dict[str, Any]],
    funds_data: list[dict[str, Any]],
    risk_profile: str,
    signal: str,
    advice: str,
    avg_pe_percentile: float | None,
) -> Path:
    """Write all market data to web/data.json and return the file path."""
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "indices": _build_indices(indices_data, valuations),
        "funds": _build_funds(funds_data),
        "recommendation": _build_recommendation(
            risk_profile, signal, advice, avg_pe_percentile,
        ),
        "market_summary": {
            "avg_pe_percentile": avg_pe_percentile,
            "overall_signal": signal,
            "overall_advice": advice,
        },
        "products": product_catalog(),
    }
    validate_dashboard_payload(payload)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(DATA_FILE.parent), suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, DATA_FILE)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    return DATA_FILE
