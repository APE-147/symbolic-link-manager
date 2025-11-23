"""Backward-compatible re-export of configuration helpers.

The concrete implementation now lives under ``slm.services.configuration`` to
align with the project-structure contract while keeping ``slm.config`` import
paths working for existing scripts and tests.
"""

from .services.configuration import (  # noqa: F401
    ConfigError,
    DEFAULT_CONFIG_LOCATIONS,
    LoadedConfig,
    coerce_scan_roots,
    load_config,
)

__all__ = [
    "ConfigError",
    "DEFAULT_CONFIG_LOCATIONS",
    "LoadedConfig",
    "coerce_scan_roots",
    "load_config",
]
