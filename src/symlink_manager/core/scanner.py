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
import unicodedata

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


console = Console(stderr=True)


def _should_exclude_symlink(name: str, exclude_patterns: Optional[List[str]]) -> bool:
    """Check if a symlink name matches any exclusion pattern.

    Uses fnmatch for glob-style pattern matching.
    """
    if not exclude_patterns:
        return False

    for pattern in exclude_patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def _is_valid_name(name: str) -> bool:
    """Check if symlink name is valid (not garbled/mojibake).

    Returns False if name contains:
    - Control characters (except newline/tab)
    - Replacement characters (�, U+FFFD)
    - Excessive non-ASCII characters (potential encoding issues)

    Args:
        name: The symlink name to validate

    Returns:
        True if the name appears valid, False if garbled
    """
    # Check for replacement character (indicates encoding error)
    if '\ufffd' in name or '�' in name:
        return False

    # Check for control characters (except tab, newline)
    for char in name:
        if unicodedata.category(char).startswith('C') and char not in '\t\n':
            return False

    # Check if name is too many non-ASCII characters (heuristic for mojibake)
    # Allow reasonable non-ASCII (for international names), but flag excessive
    non_ascii_count = sum(1 for c in name if ord(c) > 127)
    if len(name) > 0 and non_ascii_count / len(name) > 0.7:
        # More than 70% non-ASCII might be encoding issue
        return False

    return True


def _is_hash_like_name(name: str) -> bool:
    """Detect if a directory/file name looks like a random hash.

    Optimized for Dropbox-style hashes (21 chars) but also catches other hash formats.
    Uses multi-level detection strategy:
    - Level 1: Exact Dropbox hash pattern (21 chars, high diversity)
    - Level 2: Base64-like pattern (20-24 chars)
    - Level 3: General hash pattern (16-32 chars)

    Examples:
        "1R3_9ZoEWvefI4rTylIiU" → True (Dropbox hash)
        "6UA9a6LZnqYXSA8WzC-ZV" → True (Dropbox hash)
        "my-project-data" → False (normal name)
        "video-downloader" → False (normal name)
    """
    if not name or len(name) < 16:
        return False

    # Remove common separators for analysis
    clean_name = name.replace('-', '').replace('_', '')

    # Must be primarily alphanumeric
    if not clean_name.isalnum():
        return False

    # Level 1: Exact Dropbox hash pattern (highest confidence)
    # 21 characters, alphanumeric + separators, high diversity
    if len(name) == 21:
        unique_chars = len(set(clean_name.lower()))
        diversity = unique_chars / len(clean_name) if clean_name else 0

        # Dropbox hashes have very high diversity (typically >0.7)
        if diversity > 0.65:
            return True

    # Level 2: Base64-like pattern (20-24 chars)
    # Common for various hash/ID systems
    if 20 <= len(name) <= 24:
        # Check for base64 character set
        base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=-_')
        if all(c in base64_chars for c in name):
            # Must have mixed character types (not just digits)
            has_upper = any(c.isupper() for c in clean_name)
            has_lower = any(c.islower() for c in clean_name)
            has_digit = any(c.isdigit() for c in clean_name)

            # Require at least 2 types (not just digits-only)
            if (has_upper + has_lower + has_digit) < 2:
                return False

            # High diversity indicates randomness
            unique_chars = len(set(clean_name.lower()))
            diversity = unique_chars / len(clean_name) if clean_name else 0
            if diversity > 0.6:
                return True

    # Level 3: General hash pattern (16-32 chars)
    if 16 <= len(clean_name) <= 32:
        # Must have mixed case (hashes typically do)
        has_upper = any(c.isupper() for c in clean_name)
        has_lower = any(c.islower() for c in clean_name)
        has_digit = any(c.isdigit() for c in clean_name)

        if has_upper and has_lower and has_digit:
            # Very high diversity = likely hash
            unique_chars = len(set(clean_name.lower()))
            diversity = unique_chars / len(clean_name) if clean_name else 0
            if diversity > 0.7:
                return True

    # Additional heuristic: Check for "too random" character distribution
    # Real words have predictable letter frequencies, hashes don't
    if len(clean_name) >= 18:
        # Count letter frequencies
        from collections import Counter
        char_counts = Counter(clean_name.lower())

        # If no character appears more than 2 times, it's very random
        max_frequency = max(char_counts.values()) if char_counts else 0
        if max_frequency <= 2 and len(clean_name) >= 20:
            return True

    return False


@dataclass(frozen=True)
class SymlinkInfo:
    path: Path
    name: str
    target: Path
    is_broken: bool
    project: Optional[str] = None
    # Hierarchical classification (auto-detected from path structure)
    primary_category: Optional[str] = None
    secondary_category: Optional[str] = None
    project_name: Optional[str] = None


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
    exclude_patterns: Optional[List[str]] = None,
    directories_only: bool = True,
    filter_garbled: bool = True,
    filter_hash_targets: bool = True,
) -> List[SymlinkInfo]:
    """Recursively scan ``scan_path`` (up to ``max_depth``) for symlinks.

    - Does not descend into symlinked directories
    - Swallows permission and transient filesystem errors
    - Detects broken and circular links (reported via ``is_broken``)
    - Optionally filters symlinks by name using glob patterns
    - Optionally filters to only include directory symlinks
    - Optionally filters out garbled/mojibake names

    Args:
        scan_path: Root directory to scan
        max_depth: Maximum directory depth to traverse
        exclude_patterns: List of glob patterns to exclude (e.g., ["python*", "pip*"])
                         If None, no filtering is applied.
        directories_only: If True, only include symlinks pointing to directories (default: True)
        filter_garbled: If True, exclude symlinks with garbled names (default: True)
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
                        # Apply garbled name filter first
                        if filter_garbled and not _is_valid_name(entry.name):
                            continue  # Skip garbled symlinks

                        # Apply pattern filtering if patterns provided
                        if _should_exclude_symlink(entry.name, exclude_patterns):
                            continue  # Skip this symlink

                        target, is_broken = _resolve_symlink_target(entry)

                        # Skip hash-like targets (Dropbox cache-style), but never for broken links
                        if not is_broken and filter_hash_targets:
                            try:
                                if _is_hash_like_name(target.name):
                                    continue
                            except Exception:
                                # Any unexpected error in heuristic should not break the scan
                                pass

                        # Apply directory-only filter
                        if directories_only and not is_broken:
                            # Only check if target exists (not broken)
                            if not target.is_dir():
                                continue  # Skip file symlinks

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
