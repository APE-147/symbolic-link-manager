"""Filesystem summary helpers used by the CLI."""

from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path
from typing import List, Tuple


def fast_tree_summary(path: Path) -> Tuple[int, int]:
    path = Path(path)
    if not path.exists() or not path.is_dir():
        return (0, 0)

    files = 0
    total_bytes = 0
    stack: List[Path] = [path]
    while stack:
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for entry in it:
                    with suppress(FileNotFoundError, PermissionError, OSError):
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                            continue
                        if entry.is_file(follow_symlinks=False):
                            files += 1
                            with suppress(FileNotFoundError, PermissionError, OSError):
                                st = entry.stat(follow_symlinks=False)
                                total_bytes += int(getattr(st, "st_size", 0))
        except (FileNotFoundError, PermissionError, NotADirectoryError, OSError):
            continue
    return (files, total_bytes)


def format_summary_pair(curr: Tuple[int, int], new: Tuple[int, int]) -> str:
    return (
        f"summary(current=files:{curr[0]} bytes:{curr[1]}, "
        f"new=files:{new[0]} bytes:{new[1]})"
    )


__all__ = ["fast_tree_summary", "format_summary_pair"]
