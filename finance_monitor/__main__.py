"""Module execution entrypoint."""

from __future__ import annotations

try:  # pragma: no cover - import shim for direct script execution
    from .main import main
except ImportError:  # pragma: no cover
    from main import main


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

