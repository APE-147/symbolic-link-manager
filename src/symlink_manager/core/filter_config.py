"""Filter configuration module for symlink scanning.

Provides YAML-based configuration for filtering symlinks during scanning.
Supports include/exclude patterns with glob and regex matching.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import fnmatch
import re

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Default exclude patterns - applied when no config file present
DEFAULT_EXCLUDE_PATTERNS = [
    "python*",      # python, python3, python3.9, etc.
    "pip*",         # pip, pip3, etc.
    "node*",        # node, nodejs
    "npm*",         # npm, npx
    "ruby*",        # ruby, ruby2.7, etc.
    "gem*",         # gem, gem3, etc.
    ".git",         # Git directory symlinks
    "node_modules", # Node.js dependencies
    "__pycache__",  # Python cache
    ".venv",        # Python virtual environments
    "venv",         # Another common venv name
]


@dataclass
class FilterRules:
    """Compiled filter rules for symlink scanning."""
    include_patterns: List[str]
    exclude_patterns: List[str]
    ignore_case: bool = False
    use_regex: bool = False
    directories_only: bool = True  # NEW: Show only directory symlinks by default
    filter_garbled: bool = True    # NEW: Filter garbled names by default
    filter_hash_targets: bool = True  # NEW: Filter symlinks whose targets look like hashes (Dropbox cache-style)

    def should_include(self, symlink_name: str) -> bool:
        """Determine if a symlink should be included based on filter rules.

        Logic:
        1. If include patterns exist and symlink matches any, include it (override exclude)
        2. If exclude patterns exist and symlink matches any, exclude it
        3. Otherwise, include it
        """
        # Normalize for case-insensitive matching
        test_name = symlink_name.lower() if self.ignore_case else symlink_name

        # Check include patterns first (highest priority)
        if self.include_patterns:
            for pattern in self.include_patterns:
                test_pattern = pattern.lower() if self.ignore_case else pattern
                if self._matches(test_name, test_pattern):
                    return True
            # If include patterns specified but none matched, exclude
            # (unless also excluded, which we check next)

        # Check exclude patterns
        if self.exclude_patterns:
            for pattern in self.exclude_patterns:
                test_pattern = pattern.lower() if self.ignore_case else pattern
                if self._matches(test_name, test_pattern):
                    # Only exclude if not in include list
                    if self.include_patterns:
                        # Already checked includes above, didn't match
                        return False
                    return False

        # Default: include if no patterns matched exclude
        return True

    def _matches(self, text: str, pattern: str) -> bool:
        """Match text against pattern using glob or regex."""
        if self.use_regex:
            try:
                return re.search(pattern, text) is not None
            except re.error:
                # Invalid regex, skip this pattern
                return False
        else:
            # Glob matching
            return fnmatch.fnmatch(text, pattern)


def load_filter_config(config_path: Optional[Path] = None) -> FilterRules:
    """Load filter configuration from YAML file.

    Args:
        config_path: Path to filter config file. If None, tries default location
                    ~/.config/lk/filter.yml. If file doesn't exist, returns
                    default exclude patterns.

    Returns:
        FilterRules with compiled patterns

    Raises:
        ValueError: If YAML is invalid or required fields are missing
    """
    if not HAS_YAML:
        # PyYAML not installed, return defaults
        return FilterRules(
            include_patterns=[],
            exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
            ignore_case=False,
            use_regex=False,
            directories_only=True,
            filter_garbled=True,
            filter_hash_targets=True,
        )

    # Determine config file path
    if config_path is None:
        config_path = Path.home() / ".config" / "lk" / "filter.yml"
    else:
        config_path = Path(config_path)

    # If file doesn't exist, return defaults
    if not config_path.exists():
        return FilterRules(
            include_patterns=[],
            exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
            ignore_case=False,
            use_regex=False,
            directories_only=True,
            filter_garbled=True,
            filter_hash_targets=True,
        )

    # Parse YAML
    try:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in filter config: {e}")
    except Exception as e:
        raise ValueError(f"Failed to read filter config: {e}")

    if data is None:
        data = {}

    # Extract fields with validation
    include_patterns = data.get('include', {})
    if isinstance(include_patterns, dict):
        include_patterns = include_patterns.get('patterns', [])
    elif not isinstance(include_patterns, list):
        include_patterns = []

    exclude_patterns = data.get('exclude', {})
    if isinstance(exclude_patterns, dict):
        exclude_patterns = exclude_patterns.get('patterns', [])
    elif not isinstance(exclude_patterns, list):
        exclude_patterns = []

    # Merge with defaults if exclude is empty
    if not exclude_patterns:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

    ignore_case = bool(data.get('ignore_case', False))
    use_regex = bool(data.get('use_regex', False))
    directories_only = bool(data.get('directories_only', True))
    filter_garbled = bool(data.get('filter_garbled', True))
    filter_hash_targets = bool(data.get('filter_hash_targets', True))

    return FilterRules(
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        ignore_case=ignore_case,
        use_regex=use_regex,
        directories_only=directories_only,
        filter_garbled=filter_garbled,
        filter_hash_targets=filter_hash_targets,
    )


def merge_cli_patterns(
    rules: FilterRules,
    cli_include: Optional[List[str]] = None,
    cli_exclude: Optional[List[str]] = None,
) -> FilterRules:
    """Merge CLI-provided patterns with config-based rules.

    CLI patterns have highest priority and are added to existing patterns.
    """
    include_patterns = list(rules.include_patterns)
    exclude_patterns = list(rules.exclude_patterns)

    if cli_include:
        include_patterns.extend(cli_include)

    if cli_exclude:
        exclude_patterns.extend(cli_exclude)

    return FilterRules(
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        ignore_case=rules.ignore_case,
        use_regex=rules.use_regex,
        directories_only=rules.directories_only,
        filter_garbled=rules.filter_garbled,
        filter_hash_targets=rules.filter_hash_targets,
    )
