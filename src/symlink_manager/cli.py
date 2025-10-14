from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click

from . import __version__


def _default_scan_root() -> Path:
    """Best-effort default scan root.

    Prefer the user's code directory if present, else current directory.
    """
    preferred = Path("/Users/niceday/Developer/Cloud/Dropbox/-Code-")
    return preferred if preferred.exists() else Path.cwd()


def _default_config_path() -> Optional[Path]:
    # XDG-style default
    xdg = Path("~/.config/lk/projects.md").expanduser()
    return xdg if xdg.exists() else None


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="symlink-manager")
@click.option(
    "target_path",
    "--target",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, path_type=Path),
    required=False,
    help="Directory to scan for symlinks (defaults to your code folder).",
)
@click.option(
    "config_path",
    "--config",
    type=click.Path(exists=False, dir_okay=False, file_okay=True, path_type=Path),
    required=False,
    help="Markdown classification config (## Project + - pattern lines).",
)
@click.option(
    "filter_config",
    "--filter-config",
    type=click.Path(exists=False, dir_okay=False, file_okay=True, path_type=Path),
    required=False,
    help="YAML filter configuration file (default: ~/.config/lk/filter.yml).",
)
@click.option(
    "no_filter",
    "--no-filter",
    is_flag=True,
    help="Disable all filtering (show all symlinks).",
)
@click.option(
    "include_patterns",
    "--include",
    multiple=True,
    help="Include pattern (can be specified multiple times, overrides exclude).",
)
@click.option(
    "exclude_patterns",
    "--exclude",
    multiple=True,
    help="Exclude pattern (can be specified multiple times).",
)
@click.option(
    "include_files",
    "--files",
    is_flag=True,
    default=False,
    help="Include file symlinks (default: directories only).",
)
@click.option(
    "include_garbled",
    "--include-garbled",
    is_flag=True,
    default=False,
    help="Include symlinks with garbled names (default: filter them out).",
)
@click.option(
    "include_hash_targets",
    "--include-hash-targets",
    is_flag=True,
    default=False,
    help=(
        "Include symlinks whose targets look like hashes (Dropbox cache-style). "
        "By default these are filtered out."
    ),
)
@click.pass_context
def cli(
    ctx: click.Context,
    target_path: Optional[Path],
    config_path: Optional[Path],
    filter_config: Optional[Path],
    no_filter: bool,
    include_patterns: Tuple[str, ...],
    exclude_patterns: Tuple[str, ...],
    include_files: bool,
    include_garbled: bool,
    include_hash_targets: bool,
) -> None:
    """Symlink Manager CLI.

    Safe symlink scanner, classifier, and migrator.
    """
    # If no subcommand was invoked, launch the interactive TUI.
    if ctx.invoked_subcommand is None:
        from .ui.tui import run_tui  # local import to keep CLI import cost low
        from .core.filter_config import load_filter_config, merge_cli_patterns, DEFAULT_EXCLUDE_PATTERNS

        scan_root = target_path if target_path is not None else _default_scan_root()
        if not scan_root.exists():
            click.echo(f"[error] Target scan path does not exist: {scan_root}")
            ctx.exit(2)

        cfg = config_path if config_path is not None else _default_config_path()

        # Handle filtering
        if no_filter:
            # Disable all filtering
            filter_rules = None
        else:
            # Load filter config
            try:
                filter_rules = load_filter_config(filter_config)
                # Merge CLI patterns if provided
                if include_patterns or exclude_patterns:
                    filter_rules = merge_cli_patterns(
                        filter_rules,
                        cli_include=list(include_patterns) if include_patterns else None,
                        cli_exclude=list(exclude_patterns) if exclude_patterns else None,
                    )
                # Apply CLI flags for directory-only and garbled filtering
                if include_files:
                    filter_rules.directories_only = False
                if include_garbled:
                    filter_rules.filter_garbled = False
                # Apply CLI flag for hash-target filtering (opt-out)
                if include_hash_targets:
                    filter_rules.filter_hash_targets = False
            except ValueError as e:
                click.echo(f"[error] Filter config error: {e}", err=True)
                ctx.exit(2)

        code = run_tui(
            scan_path=scan_root,
            config_path=cfg,
            filter_rules=filter_rules,
        )
        ctx.exit(code)


@cli.command()
def version() -> None:
    """Print the version and exit."""
    click.echo(__version__)


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point for console_scripts.

    Returns process exit code (0 for success).
    """
    try:
        cli.main(args=argv, prog_name="lk", standalone_mode=False)
    except SystemExit as exc:
        return int(exc.code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
