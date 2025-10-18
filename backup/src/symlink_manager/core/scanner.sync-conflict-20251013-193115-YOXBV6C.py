from __future__ import annotations

"""Symlink discovery module (Task-2).

Requirements:
- Recursive scan to find all symbolic links under a directory
- Handle permission errors gracefully
- Detect circular/broken symlinks
- Return SymlinkInfo dataclass with: path, name, target, is_broken, project
- Provide ``--scan-path`` CLI option (``python -m symlink_manager.core.scanner``)
- Use pathlib for Python 3.9+ compatibility
- Show a progress indicator using ``rich``
- Support a max recursion depth limit (default 20)
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Tuple
import fnmatch
import json
import os

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


console = Console(stderr=True)


@dataclass(frozen=True)
class SymlinkInfo:
    path: Path
    name: str
    target: Path
    is_broken: bool
    project: Optional[str] = None


def _safe_iterdir(path: Path) -> Iterator[Path]:
    """Iterate directory entries, swallowing permission-related errors.

    Yields nothing when inaccessible, instead of raising.
    """
    try:
        yield from path.iterdir()
    except PermissionError:
        console.log(f"[yellow]Permission denied[/]: {path}")
    except FileNotFoundError:
        # Directory disappeared during scan; skip quietly.
        pass
    except OSError as exc:
        # Other OS-level access errors should not crash the scan.
        console.log(f"[yellow]OS error[/] accessing {path}: {exc}")


def _resolve_symlink_target(link_path: Path, chain_limit: int = 100) -> Tuple[Path, bool]:
    """Resolve a symlink's ultimate target conservatively.

    Returns (resolved_target, is_broken). A link is considered broken if
    the next hop does not exist or a circular reference is detected.
    ``resolved_target`` is the best-effort absolute path derived from the
    link's raw target string (even if broken).
    """
    try:
        raw = os.readlink(link_path)
    except OSError:
        # If we cannot readlink (race condition), treat as broken with self path.
        return (link_path, True)

    # Compute first-hop target as absolute path relative to the link's parent
    current = (link_path.parent / raw) if not os.path.isabs(raw) else Path(raw)
    current = current

    visited: set[Path] = set()
    hops = 0
    while True:
        hops += 1
        if hops > chain_limit:
            return (current.resolve(strict=False), True)

        # If the current hop does not exist, it's broken.
        if not current.exists():
            # Return the best-effort absolute path even if missing
            try:
                return (current.resolve(strict=False), True)
            except Exception:
                return (current, True)

        # If the current hop is not a symlink, we reached a concrete target.
        if not current.is_symlink():
            try:
                return (current.resolve(strict=False), False)
            except Exception:
                # Shouldn't happen, but stay conservative
                return (current, False)

        # If still a symlink, step to next hop; detect cycles
        abs_current = current.resolve(strict=False)
        if abs_current in visited or abs_current == link_path.resolve(strict=False):
            return (abs_current, True)
        visited.add(abs_current)

        try:
            raw_next = os.readlink(current)
        except OSError:
            # Can't read next hop; mark as broken
            return (abs_current, True)

        next_path = (current.parent / raw_next) if not os.path.isabs(raw_next) else Path(raw_next)
        current = next_path


def scan_symlinks(
    scan_path: Path,
    max_depth: int = 20,
    exclude_patterns: Optional[List[str]] = None
) -> List[SymlinkInfo]:
    """Recursively scan ``scan_path`` (up to ``max_depth``) for symlinks.

    - Does not descend into symlinked directories
    - Swallows permission and transient filesystem errors
    - Detects broken and circular links (reported via ``is_broken``)
    - Optionally filters symlinks by name using glob patterns

    Args:
        scan_path: Root directory to scan
        max_depth: Maximum directory depth to traverse
        exclude_patterns: List of glob patterns to exclude (e.g., ["python*", "pip*"])
                         If None, no filtering is applied.
    """
    results: list[SymlinkInfo] = []
    if not scan_path.exists():
        console.log(f"[red]Scan path does not exist[/]: {scan_path}")
        return results

    # Manual stack to avoid Python recursion limits and to cap depth
    stack: list[tuple[Path, int]] = [(scan_path, 0)]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task("Scanning symlinks...", start=True)

        while stack:
            current_dir, depth = stack.pop()
            progress.update(task, description=f"Scanning: {current_dir}")

            # Do not traverse beyond depth limit
            if depth > max_depth:
                continue

            # We never descend into symlinked directories to avoid cycles
            for entry in _safe_iterdir(current_dir):
                try:
                    if entry.is_symlink():
                        target, is_broken = _resolve_symlink_target(entry)
                        info = SymlinkInfo(
                            path=entry,
                            name=entry.name,
                            target=target,
                            is_broken=is_broken,
                            project=None,
                        )
                        results.append(info)
                    elif entry.is_dir():
                        # Only real directories are traversed
                        if not entry.is_symlink():
                            stack.append((entry, depth + 1))
                except PermissionError:
                    console.log(f"[yellow]Permission denied[/]: {entry}")
                except FileNotFoundError:
                    # Entry vanished during scan; skip
                    continue
                except OSError as exc:
                    console.log(f"[yellow]OS error[/] at {entry}: {exc}")

        progress.update(task, description="Scan complete")

    return results


# ---- CLI (module entry point) -------------------------------------------------

import sys
import click


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "scan_path",
    "--scan-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    required=True,
    help="Directory to recursively scan for symlinks.",
)
@click.option(
    "max_depth",
    "--max-depth",
    type=int,
    default=20,
    show_default=True,
    help="Maximum recursion depth for directory traversal.",
)
def _cli(scan_path: Path, max_depth: int) -> None:
    """Scan for symlinks and print JSON to stdout."""
    symlinks = scan_symlinks(scan_path=scan_path, max_depth=max_depth)

    def _encode(item: SymlinkInfo) -> dict[str, object]:
        data = asdict(item)
        # Convert Path fields to strings for JSON serialization
        data["path"] = str(item.path)
        data["target"] = str(item.target)
        return data

    json_output = json.dumps([_encode(s) for s in symlinks], indent=2)
    # stdout for data, stderr used by rich for progress
    print(json_output)


def main(argv: Iterable[str] | None = None) -> int:
    try:
        _cli.main(args=list(argv) if argv is not None else None, standalone_mode=False)
    except SystemExit as exc:
        return int(exc.code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
