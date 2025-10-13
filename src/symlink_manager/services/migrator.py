from __future__ import annotations

"""Safe migration and backup services.

This is a placeholder implementation for Task-6.
"""

from pathlib import Path


def plan_migration(source: Path, dest: Path) -> dict[str, str]:
    """Return a dry-run plan for migrating ``source`` to ``dest``.

    Placeholder to define the interface only.
    """
    return {"source": str(source), "dest": str(dest), "action": "noop"}

