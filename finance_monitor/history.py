"""Persistence helpers for market snapshots."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

try:  # pragma: no cover - import shim for direct script execution
    from .config import HISTORY_FILE, HISTORY_LIMIT
except ImportError:  # pragma: no cover
    from config import HISTORY_FILE, HISTORY_LIMIT

HistoryRecord = dict[str, Any]
HistoryMap = dict[str, list[HistoryRecord]]


def _resolve_path(history_file: str | Path | None = None) -> Path:
    return Path(HISTORY_FILE if history_file is None else history_file)


def _backup_path(path: Path) -> Path:
    return Path(f"{path}.bak")


def _normalize_history(raw: Any) -> HistoryMap:
    if not isinstance(raw, dict):
        return {}

    history: HistoryMap = {}
    for name, records in raw.items():
        if not isinstance(records, list):
            continue
        cleaned: list[HistoryRecord] = []
        for record in records:
            if isinstance(record, dict):
                cleaned.append(record)
        if cleaned:
            history[str(name)] = cleaned
    return history


def load_history(history_file: str | Path | None = None) -> HistoryMap:
    """Load history from disk and back up corrupted files when needed."""
    path = _resolve_path(history_file)
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except json.JSONDecodeError:
        backup = _backup_path(path)
        try:
            os.replace(path, backup)
        except OSError:
            pass
        return {}
    except OSError:
        return {}

    return _normalize_history(raw)


def _write_history_atomic(path: Path, history: HistoryMap) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(history, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def save_history(
    index_name: str,
    pe_percentile: float,
    pe: float,
    close: float,
    *,
    history_file: str | Path | None = None,
    date: str | None = None,
    max_entries: int = HISTORY_LIMIT,
) -> HistoryMap:
    """Persist one market snapshot and keep the file compact."""
    path = _resolve_path(history_file)
    history = load_history(path)

    today = date or datetime.now().strftime("%Y-%m-%d")
    records = history.setdefault(str(index_name), [])
    records = [record for record in records if record.get("date") != today]
    records.append(
        {
            "date": today,
            "pe": pe,
            "pe_percentile": pe_percentile,
            "close": close,
        }
    )
    history[str(index_name)] = records[-max_entries:]
    _write_history_atomic(path, history)
    return history

