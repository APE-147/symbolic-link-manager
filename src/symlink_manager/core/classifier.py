from __future__ import annotations

"""Markdown-driven symlink classification (Task-3).

This module parses a simple Markdown configuration to classify discovered
symlinks into project buckets by matching glob patterns against symlink
paths. Unmatched links are grouped under the ``unclassified`` category.

Config format (order matters; first match wins):

    ## ProjectName
    - pattern/glob/*
    - another/path/**

Parsing is tolerant: missing/invalid config gracefully falls back to
putting all links into ``unclassified``.
"""

from collections import OrderedDict
from dataclasses import replace, asdict
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional
import fnmatch
import json

from rich.console import Console

from .scanner import SymlinkInfo, scan_symlinks


console = Console(stderr=True)


# ---- Config parsing ----------------------------------------------------------

ConfigMap = "OrderedDict[str, list[str]]"


def _iter_lines(text: str) -> Iterator[str]:
    for raw in text.splitlines():
        yield raw.rstrip("\n")


def parse_markdown_config_text(text: str) -> "OrderedDict[str, list[str]]":
    """Parse Markdown text into an ordered mapping of project → patterns.

    Only headers starting with ``## `` are treated as project names. Bullet
    lines starting with ``- `` within a project section are collected as
    shell-style glob patterns (``fnmatch`` semantics). Other content is
    ignored.
    """
    config: "OrderedDict[str, list[str]]" = OrderedDict()
    current: Optional[str] = None

    for line in _iter_lines(text):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("## "):
            current = stripped[3:].strip()
            if current and current not in config:
                config[current] = []
            continue
        if stripped.startswith("- ") and current:
            pat = stripped[2:].strip()
            if pat:
                config[current].append(pat)

    # Ensure all projects exist even if they ended up with no patterns
    return config


def load_markdown_config(path: Optional[Path]) -> "OrderedDict[str, list[str]]":
    """Load and parse Markdown config from ``path``.

    On any error (None, missing file, decode error), returns an empty mapping
    so that classification can gracefully fall back to ``unclassified``.
    """
    if path is None:
        return OrderedDict()
    try:
        text = Path(path).read_text(encoding="utf-8")
    except Exception as exc:
        console.log(f"[yellow]Config not loaded[/]: {path} ({exc})")
        return OrderedDict()
    try:
        return parse_markdown_config_text(text)
    except Exception as exc:  # Defensive; parser is intentionally simple
        console.log(f"[yellow]Invalid config format[/]: {path} ({exc})")
        return OrderedDict()


# ---- Classification ----------------------------------------------------------

def _path_variants(p: Path, scan_root: Optional[Path]) -> List[str]:
    """Return string variants for glob matching (abs and relative, POSIX style).

    Important: We match on the symlink path itself, not its resolved target.
    """
    variants: list[str] = []
    # Absolute path of the link (without resolving)
    abs_posix = p.as_posix()
    variants.append(abs_posix)
    if scan_root is not None:
        try:
            rel = p.relative_to(scan_root)
            variants.append(rel.as_posix())
        except Exception:
            # Not under scan root; ignore relative variant
            pass
    # Also include the name for convenience
    variants.append(p.name)
    return variants


def classify_symlinks(
    symlinks: List[SymlinkInfo],
    config: "OrderedDict[str, list[str]]",
    *,
    scan_root: Optional[Path] = None,
) -> Dict[str, List[SymlinkInfo]]:
    """Classify ``symlinks`` into project buckets per Markdown ``config``.

    - Glob patterns use ``fnmatch`` against absolute path, relative-to-``scan_root``
      (when provided), and file name variants. The first matching pattern across
      the config's declared order determines the project.
    - Returns a mapping that includes all projects from the config (possibly
      empty lists) plus the ``unclassified`` bucket.
    - Each returned ``SymlinkInfo`` is a copy with ``project`` set.
    """
    # Initialize result buckets for all declared projects to preserve order
    result: Dict[str, List[SymlinkInfo]] = {k: [] for k in config.keys()}
    result.setdefault("unclassified", [])

    for item in symlinks:
        variants = _path_variants(item.path, scan_root)

        matched_project: Optional[str] = None
        for project, patterns in config.items():
            for pat in patterns:
                if any(fnmatch.fnmatch(v, pat) for v in variants):
                    matched_project = project
                    break
            if matched_project:
                break

        if matched_project is None:
            result["unclassified"].append(item)
        else:
            result[matched_project].append(replace(item, project=matched_project))

    return result


# ---- Hierarchical Classification with Auto-Detection ------------------------

def _extract_path_hierarchy(symlink_path: Path, scan_root: Path) -> tuple[str, str]:
    """Extract Level 2 (folder) and Level 3 (project) from path structure.

    Args:
        symlink_path: Full path to symlink
        scan_root: Scan root directory

    Returns:
        (secondary_category, project_name)

    Example:
        symlink_path = /Users/me/Developer/Desktop/Projects/MyApp/data
        scan_root = /Users/me/Developer
        → ("Desktop", "Projects")

        symlink_path = /Users/me/Desktop/Tools/ToolX/config
        scan_root = /Users/me/Desktop
        → ("Tools", "ToolX")
    """
    try:
        # Get relative path from scan root
        rel_path = symlink_path.relative_to(scan_root)
        parts = rel_path.parts

        if len(parts) == 0:
            return ("unclassified", "unclassified")
        elif len(parts) == 1:
            # Symlink directly under scan_root
            return ("root", symlink_path.name)
        elif len(parts) == 2:
            # scan_root/folder/symlink
            return (parts[0], symlink_path.name)
        else:
            # scan_root/category/folder/project/symlink
            # Use first part as secondary, second as project
            secondary = parts[0]
            project = parts[1]
            return (secondary, project)

    except ValueError:
        # Path not relative to scan_root, use parent directories
        parent = symlink_path.parent
        grandparent = parent.parent if parent.parent != parent else None

        if grandparent and grandparent != parent:
            return (parent.name, symlink_path.name)
        else:
            return (parent.name, symlink_path.name)


def _detect_hierarchy_from_primary(
    symlink_path: Path,
    primary_match_pattern: str
) -> tuple[str, str]:
    """Extract hierarchy based on where primary pattern matched.

    Args:
        symlink_path: /Users/me/Desktop/Projects/MyApp/data
        primary_match_pattern: /Users/*/Desktop/**/*

    Returns:
        (secondary, project)

    Logic:
        1. Find where pattern matched (e.g., /Users/me/Desktop/)
        2. Extract remaining path parts (Projects/MyApp/data)
        3. First part = secondary, second part = project
    """
    # Strip trailing glob patterns to get the base pattern
    base_pattern = primary_match_pattern
    for suffix in ["/**/*", "/**", "/*", "*"]:
        if base_pattern.endswith(suffix):
            base_pattern = base_pattern[:-len(suffix)]
            break

    # Convert pattern to parts for matching
    pattern_parts = list(Path(base_pattern).parts)
    path_parts = list(symlink_path.parts)

    # Find where the pattern matches in the path
    match_end_idx = None
    for i in range(len(path_parts) - len(pattern_parts) + 1):
        matched = True
        for j, pattern_part in enumerate(pattern_parts):
            if pattern_part == "*" or pattern_part == "**":
                continue
            if i + j >= len(path_parts) or pattern_part != path_parts[i + j]:
                matched = False
                break
        if matched:
            match_end_idx = i + len(pattern_parts)
            break

    if match_end_idx is None or match_end_idx >= len(path_parts):
        # Fallback to parent/grandparent
        return (symlink_path.parent.name, symlink_path.name)

    # Extract parts after match
    remaining_parts = path_parts[match_end_idx:]

    if len(remaining_parts) == 0:
        return ("root", symlink_path.name)
    elif len(remaining_parts) == 1:
        return ("root", remaining_parts[0])
    else:
        return (remaining_parts[0], remaining_parts[1])


def _matches_pattern(symlink: SymlinkInfo, pattern: str, scan_root: Optional[Path]) -> bool:
    """Check if symlink matches a pattern (reusing existing logic)."""
    variants = _path_variants(symlink.path, scan_root)

    # Expand ~ in pattern to home directory
    if pattern.startswith("~/"):
        pattern = str(Path.home()) + pattern[1:]

    for variant in variants:
        if fnmatch.fnmatch(variant, pattern):
            return True
    return False


def classify_symlinks_auto_hierarchy(
    symlinks: List[SymlinkInfo],
    config: "OrderedDict[str, list[str]]",
    *,
    scan_root: Path
) -> Dict[str, Dict[str, List[SymlinkInfo]]]:
    """Classify symlinks with auto-detected hierarchy.

    Level 1: Manual (from config - primary category names)
    Level 2 & 3: Auto-detected from path structure

    Args:
        symlinks: List of discovered symlinks
        config: Simplified config mapping primary_name → patterns
        scan_root: Root directory for path calculations

    Returns:
        {
            "Desktop": {
                "Projects": [symlink1, symlink2, ...],
                "Tools": [symlink3, ...]
            },
            "Service": {...},
            "System": {...},
            "unclassified": {"unclassified": [...]}
        }
    """
    result: Dict[str, Dict[str, List[SymlinkInfo]]] = {}

    for symlink in symlinks:
        matched_primary = None
        matched_pattern = None

        # Step 1: Match Level 1 (Primary Category) from config
        for primary_name, patterns in config.items():
            for pattern in patterns:
                if _matches_pattern(symlink, pattern, scan_root):
                    matched_primary = primary_name
                    matched_pattern = pattern
                    break
            if matched_primary:
                break

        # If no Level 1 match, put in unclassified
        if not matched_primary:
            matched_primary = "unclassified"
            secondary = "unclassified"
            project = symlink.name
        else:
            # Step 2: Auto-detect Level 2 & 3 from path structure
            secondary, project = _detect_hierarchy_from_primary(
                symlink.path,
                matched_pattern
            )

        # Step 3: Update symlink with hierarchy info
        symlink_with_hierarchy = replace(
            symlink,
            primary_category=matched_primary,
            secondary_category=secondary,
            project_name=project,
            project=matched_primary  # Maintain backward compat
        )

        # Step 4: Add to result structure
        if matched_primary not in result:
            result[matched_primary] = {}
        if secondary not in result[matched_primary]:
            result[matched_primary][secondary] = []

        result[matched_primary][secondary].append(symlink_with_hierarchy)

    return result


# ---- CLI (module entry point) -----------------------------------------------

import sys
import click


def _encode(item: SymlinkInfo) -> dict:
    data = asdict(item)
    data["path"] = str(item.path)
    data["target"] = str(item.target)
    return data


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "config_path",
    "--config",
    type=click.Path(exists=False, dir_okay=False, file_okay=True, path_type=Path),
    required=False,
    help="Path to Markdown classification config (## Project + - pattern lines).",
)
@click.option(
    "scan_path",
    "--scan-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    default=Path("."),
    show_default=True,
    help="Directory to recursively scan for symlinks before classifying.",
)
@click.option(
    "max_depth",
    "--max-depth",
    type=int,
    default=20,
    show_default=True,
    help="Maximum recursion depth for directory traversal.",
)
def _cli(config_path: Optional[Path], scan_path: Path, max_depth: int) -> None:
    """Scan + classify symlinks, printing JSON mapping of categories to items."""
    config = load_markdown_config(config_path)
    if not config:
        console.log("[yellow]No valid config provided; all items will be unclassified.")

    symlinks = scan_symlinks(scan_path=scan_path, max_depth=max_depth)
    buckets = classify_symlinks(symlinks, config, scan_root=scan_path)

    json_ready: dict[str, list[dict]] = {}
    for k, items in buckets.items():
        json_ready[k] = [_encode(i) for i in items]
    print(json.dumps(json_ready, indent=2))


def main(argv: Iterable[str] | None = None) -> int:
    try:
        _cli.main(args=list(argv) if argv is not None else None, standalone_mode=False)
    except SystemExit as exc:
        return int(exc.code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
