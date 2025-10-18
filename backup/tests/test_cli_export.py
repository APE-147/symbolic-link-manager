from __future__ import annotations

from pathlib import Path
import os
import json

from symlink_manager.cli import main as cli_main


def _make_dir_symlink(base: Path, name: str) -> tuple[Path, Path]:
    target = base / f"{name}_target"
    target.mkdir(parents=True, exist_ok=True)
    link = base / name
    os.symlink(target, link)
    return link, target


def test_export_hierarchical_json(tmp_path: Path, capfd) -> None:
    # Arrange: create a small hierarchy and a config that matches tmp_path
    root = tmp_path
    (root / "Projects" / "MyApp").mkdir(parents=True, exist_ok=True)
    (root / "Tools" / "ToolX").mkdir(parents=True, exist_ok=True)

    # Two directory symlinks under different secondary/project folders
    _make_dir_symlink(root / "Projects" / "MyApp", "data")
    _make_dir_symlink(root / "Tools" / "ToolX", "config")

    # Config that treats tmp_path as a single primary ("Desktop")
    cfg = root / "config.md"
    cfg.write_text(f"## Desktop\n- {root.as_posix()}/**/*\n", encoding="utf-8")

    # Act: run `lk export` via CLI main
    rc = cli_main([
        "export",
        "--target",
        str(root),
        "--config",
        str(cfg),
        "--pretty",  # ensure pretty for stable assertions
    ])
    assert rc == 0

    out, err = capfd.readouterr()
    assert err.strip() == ""

    data = json.loads(out)

    # Assert: hierarchical keys present and items encoded
    assert "Desktop" in data
    desktop = data["Desktop"]
    # Secondary buckets
    assert "Projects" in desktop
    assert "Tools" in desktop
    # Each bucket should have at least one encoded item with expected fields
    one = desktop["Projects"][0]
    assert one["primary_category"] == "Desktop"
    assert one["secondary_category"] == "Projects"
    assert one["project_name"] == "MyApp"
    assert isinstance(one["path"], str)
    assert isinstance(one["target"], str)


def test_export_flat_json(tmp_path: Path, capfd) -> None:
    # Arrange: one directory symlink, no config → unclassified bucket
    link, _ = _make_dir_symlink(tmp_path, "alpha")

    # Act: flat export
    rc = cli_main([
        "export",
        "--target",
        str(tmp_path),
        "--flat",
        "--pretty",
    ])
    assert rc == 0
    out, err = capfd.readouterr()
    assert err.strip() == ""

    data = json.loads(out)
    assert "unclassified" in data
    items = data["unclassified"]
    assert any(Path(i["path"]).name == link.name for i in items)
