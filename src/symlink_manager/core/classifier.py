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
