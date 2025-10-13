from __future__ import annotations

from pathlib import Path
import os

import pytest

from symlink_manager.core.scanner import scan_symlinks, SymlinkInfo


def _names(items: list[SymlinkInfo]) -> set[str]:
    return {i.name for i in items}


def test_scanner_finds_symlink(tmp_path: Path) -> None:
    target = tmp_path / "real.txt"
    target.write_text("hello")

    link = tmp_path / "link.txt"
    os.symlink(target, link)

    results = scan_symlinks(tmp_path)
    assert len(results) == 1
    info = results[0]
    assert info.path == link
    assert info.name == "link.txt"
    assert info.is_broken is False
    assert Path(info.target) == target
    assert info.project is None


def test_scanner_flags_broken_symlink(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    link = tmp_path / "broken_link"
    os.symlink(missing, link)

    results = scan_symlinks(tmp_path)
    assert _names(results) == {"broken_link"}
    info = results[0]
    assert info.is_broken is True
    # Target path should still serialize to the intended (absolute) path
    assert Path(info.target).name == "missing.txt"


def test_scanner_detects_circular_symlink(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    os.symlink(b.name, a)  # relative link to b
    os.symlink(a.name, b)  # relative link to a

    results = scan_symlinks(tmp_path)
    names = _names(results)
    assert names == {"a", "b"}

    by_name = {i.name: i for i in results}
    assert by_name["a"].is_broken is True
    assert by_name["b"].is_broken is True


def test_scanner_handles_permission_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Create an unreadable directory and ensure scanner does not crash
    protected = tmp_path / "no_access"
    protected.mkdir()

    original_iterdir = Path.iterdir

    def guarded_iterdir(self: Path):  # type: ignore[override]
        if self == protected:
            raise PermissionError("permission denied for test")
        return original_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", guarded_iterdir, raising=True)

    # Create a real symlink elsewhere to ensure we still collect results
    target = tmp_path / "ok.txt"
    target.write_text("data")
    link = tmp_path / "ok_link"
    os.symlink(target, link)

    results = scan_symlinks(tmp_path)
    # We should find the good link and not crash due to the protected dir
    assert _names(results) == {"ok_link"}

