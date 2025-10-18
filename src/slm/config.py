from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover - exercised when dependency missing
    yaml = None
    _yaml_import_error = exc
else:
    _yaml_import_error = None


class ConfigError(RuntimeError):
    """Raised when configuration loading fails."""


DEFAULT_CONFIG_LOCATIONS: Tuple[Path, ...] = (Path("~/.config/slm.yml"),)


@dataclass(frozen=True)
class LoadedConfig:
    data: Dict[str, Any]
    path: Optional[Path]


def _ensure_yaml_available() -> None:
    if yaml is None:
        raise ConfigError(
            "PyYAML is required for configuration files. "
            "Install the 'PyYAML' package to enable config support."
        ) from _yaml_import_error


def _load_yaml(path: Path) -> Dict[str, Any]:
    _ensure_yaml_available()
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - filesystem errors
        raise ConfigError(f"无法读取配置文件：{path}") from exc
    try:
        parsed = yaml.safe_load(content) if content.strip() else {}
    except Exception as exc:
        raise ConfigError(f"解析配置文件失败：{path}") from exc
    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise ConfigError(f"配置文件必须是键值对象：{path}")
    return {str(k): v for k, v in parsed.items()}


def load_config(
    candidates: Optional[Iterable[Path]] = None,
) -> LoadedConfig:
    """Load configuration data from the first existing path.

    Returns an empty configuration if none of the candidates exist.
    """
    paths = list(candidates) if candidates is not None else list(DEFAULT_CONFIG_LOCATIONS)
    for raw in paths:
        candidate = raw.expanduser().resolve()
        if not candidate.exists():
            continue
        data = _load_yaml(candidate)
        return LoadedConfig(data=data, path=candidate)
    return LoadedConfig(data={}, path=None)


def coerce_scan_roots(value: Any, *, context: str) -> List[str]:
    """Validate the scan_roots value loaded from configuration."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        items: List[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ConfigError(f"{context} 中的 scan_roots 必须是字符串路径。")
            items.append(item)
        return items
    raise ConfigError(f"{context} 中的 scan_roots 类型不受支持。")

