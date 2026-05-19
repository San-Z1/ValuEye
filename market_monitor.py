"""Legacy compatibility wrapper for the modern package entrypoint."""

from __future__ import annotations

from finance_monitor.main import main


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
