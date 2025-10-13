# Stack Fingerprint

## Language & Runtime
- **Primary Language**: Python 3.x
- **Target Version**: Python ≥3.9 (for pathlib, type hints, modern features)
- **Package Manager**: pip / pipx

## Core Dependencies
- **click**: CLI framework (argument parsing, commands, decorators)
- **rich**: Terminal UI library (styling, tables, progress, prompts, panels)
- **pathlib**: Built-in (filesystem operations)

## Development Tools
- **Build System**: setuptools / hatchling (via pyproject.toml)
- **Testing**: pytest, pytest-cov (coverage)
- **Linting**: ruff (modern Python linter/formatter)
- **Type Checking**: mypy (optional, recommended for production)

## Detected Commands
Based on the chosen stack:
- **Install**: `pipx install .` or `pipx install -e .` (editable)
- **Run**: `link` (global command after installation)
- **Test**: `pytest tests/ -v --cov=src/symbolic_link_changer`
- **Lint**: `ruff check src/ tests/`
- **Format**: `ruff format src/ tests/`
- **Type Check**: `mypy src/`

## Project Structure (per ⑤)
```
symbolic_link_changer/
├── pyproject.toml          # PEP 621 metadata + dependencies
├── README.md
├── CHANGELOG.md
├── AGENTS.md
├── .env.example            # Config template (if needed)
├── src/
│   └── symbolic_link_changer/
│       ├── __init__.py
│       ├── cli.py          # Click entry point
│       ├── core/           # Domain logic
│       │   ├── __init__.py
│       │   ├── scanner.py  # Symlink discovery
│       │   └── modifier.py # Symlink modification
│       ├── services/       # Application services
│       │   ├── __init__.py
│       │   └── classifier.py # Classification logic
│       └── utils/          # Utilities
│           ├── __init__.py
│           └── paths.py    # Path helpers
├── docs/
│   ├── REQUIRES.md
│   ├── PLAN.md
│   ├── TASKS.md
│   ├── FEATURE_SPEC.md
│   ├── blast-radius.md
│   └── stack-fingerprint.md (this file)
├── data/                   # Runtime output (gitignored)
│   ├── backups/            # Symlink backups
│   └── logs/               # Operation logs
└── tests/
    ├── __init__.py
    ├── test_scanner.py
    ├── test_classifier.py
    ├── test_modifier.py
    └── fixtures/           # Test data
```

## Installation Methods
1. **Development**: `pipx install -e .` (editable, for development)
2. **Production**: `pipx install .` (from source)
3. **Future**: `pipx install symbolic-link-changer` (from PyPI)

## Quality Gate Tools
- **pytest**: Unit and integration tests
- **pytest-cov**: Code coverage reporting (target: ≥80%)
- **ruff**: Fast Python linter and formatter (replaces flake8, black, isort)
- **mypy**: Static type checking (optional but recommended)

## Compatibility
- **OS**: macOS (primary), Linux (should work), Windows (symlink support varies)
- **Python**: 3.9+ (using modern pathlib and type hints)
- **Terminal**: ANSI color support required for Rich (most modern terminals)

## Notes
- Using `pipx` ensures isolated environment (no dependency conflicts)
- `rich` provides TUI capabilities without heavier frameworks like Textual
- `click` is industry standard for CLI applications
- `ruff` is significantly faster than traditional linters
- No database required (filesystem operations only)
