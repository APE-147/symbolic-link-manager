from __future__ import annotations

import sys
from typing import Optional

import click

from . import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="symlink-manager")
def cli() -> None:
    """Symlink Manager CLI.

    Safe symlink scanner, classifier, and migrator.
    """


@cli.command()
def version() -> None:
    """Print the version and exit."""
    click.echo(__version__)


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point for console_scripts.

    Returns process exit code (0 for success).
    """
    try:
        cli.main(args=argv, prog_name="link", standalone_mode=False)
    except SystemExit as exc:
        return int(exc.code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

