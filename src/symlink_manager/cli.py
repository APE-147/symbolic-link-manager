from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

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
@click.pass_context
def cli(ctx: click.Context, target_path: Optional[Path], config_path: Optional[Path]) -> None:
    """Symlink Manager CLI.

    Safe symlink scanner, classifier, and migrator.
    """
    # If no subcommand was invoked, launch the interactive TUI.
    if ctx.invoked_subcommand is None:
        from .ui.tui import run_tui  # local import to keep CLI import cost low

        scan_root = target_path if target_path is not None else _default_scan_root()
        if not scan_root.exists():
            click.echo(f"[error] Target scan path does not exist: {scan_root}")
            ctx.exit(2)

        cfg = config_path if config_path is not None else _default_config_path()
        code = run_tui(scan_path=scan_root, config_path=cfg)
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
