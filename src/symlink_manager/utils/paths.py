from __future__ import annotations

"""Path-related helpers (placeholder)."""

from pathlib import Path
from typing import Union


def expand(path: Union[str, Path]) -> Path:
    p = Path(path).expanduser()
    try:
        return p.resolve()
    except Exception:
        # Best-effort resolution; return expanded path on failure
        return p
