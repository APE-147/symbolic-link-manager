from __future__ import annotations

"""Symlink discovery module.

This is a placeholder implementation for Task-2.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional


@dataclass(frozen=True)
class LinkInfo:
    path: Path
    target: Optional[Path]


def iter_symlinks(root: Path) -> Iterator[LinkInfo]:
    """Yield symlink entries under ``root`` (non-destructive).

    Placeholder: structure only; real logic to be implemented in Task-2.
    """
    if not root.exists():
        return iter(())
    # Future: walk filesystem, handle permissions, etc.
    return iter(())


def main(argv: Iterable[str] | None = None) -> int:
    # Placeholder CLI for module-level execution in later tasks
    # Kept minimal for now.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
