"""Version metadata for slm."""

__version__ = "0.1.0"


def get_version() -> str:
    return __version__


__all__ = ["__version__", "get_version"]
