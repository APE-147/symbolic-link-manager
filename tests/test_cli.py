import os
import time
from pathlib import Path

import pytest

from slm import cli
from slm.cli import MigrationError, _derive_backup_path, _safe_move_dir, migrate_target_and_update_links
from slm.config import LoadedConfig


class DummyPrompt:
    def __init__(self, value):
        self._value = value

    def ask(self):
        return self._value


def test_derive_backup_path_unique(tmp_path):
    target = tmp_path / "data_folder"
    target.mkdir()
    fixed_now = 1_700_000_000
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(fixed_now))

    first_candidate = _derive_backup_path(target, now=fixed_now)
    assert first_candidate == target.with_name(f"{target.name}~{timestamp}")

    first_candidate.mkdir()
    second_candidate = _derive_backup_path(target, now=fixed_now)
    assert second_candidate == target.with_name(f"{target.name}~{timestamp}-1")


def test_migrate_abort_when_destination_exists(tmp_path):
    current_target = tmp_path / "current"
    current_target.mkdir()
    (current_target / "file.txt").write_text("alpha")

    new_target = tmp_path / "existing"
    new_target.mkdir()

    link_dir = tmp_path / "links"
    link_dir.mkdir()
    link_path = link_dir / "link"
    link_path.symlink_to(current_target)

    with pytest.raises(MigrationError):
        migrate_target_and_update_links(current_target, new_target, [link_path], dry_run=False)

    assert link_path.resolve() == current_target
    assert current_target.exists()
    assert new_target.exists()


def test_migrate_with_backup_strategy(tmp_path):
    current_target = tmp_path / "data" / "target"
    current_target.mkdir(parents=True)
    (current_target / "payload.txt").write_text("payload")

    new_target = tmp_path / "data" / "destination"
    new_target.mkdir()
    (new_target / "keep.txt").write_text("keep")

    backup_path = tmp_path / "data" / "destination-backup"

    link_dir = tmp_path / "links"
    link_dir.mkdir()
    link_path = link_dir / "alias"
    link_path.symlink_to(current_target)

    plan = migrate_target_and_update_links(
        current_target,
        new_target,
        [link_path],
        dry_run=True,
        conflict_strategy="backup",
        backup_path=backup_path,
    )
    assert any("Backup" in line for line in plan)

    migrate_target_and_update_links(
        current_target,
        new_target,
        [link_path],
        dry_run=False,
        conflict_strategy="backup",
        backup_path=backup_path,
    )

    assert backup_path.exists()
    assert (backup_path / "keep.txt").read_text() == "keep"
    assert new_target.exists()
    assert (new_target / "payload.txt").read_text() == "payload"
    assert not current_target.exists()
    assert Path(os.readlink(link_path)) == new_target
    assert link_path.resolve() == new_target


def test_main_dry_run_and_apply(tmp_path, monkeypatch, capsys):
    data_root = tmp_path / "Developer" / "Data"
    target = data_root / "project"
    target.mkdir(parents=True)
    (target / "data.txt").write_text("123")

    new_target_parent = tmp_path / "Migrated"
    new_target_parent.mkdir()
    new_target = new_target_parent / "project"

    link_root = tmp_path / "links"
    link_root.mkdir()
    link_path = link_root / "project-link"
    link_path.symlink_to(target)

    select_answers = [target]
    text_answers = [str(new_target)]
    confirm_answers = [True]

    monkeypatch.setattr(cli, "load_config", lambda: LoadedConfig(data={}, path=None))

    def fake_select(*args, **kwargs):
        return DummyPrompt(select_answers.pop(0))

    def fake_text(*args, **kwargs):
        return DummyPrompt(text_answers.pop(0))

    def fake_confirm(*args, **kwargs):
        return DummyPrompt(confirm_answers.pop(0))

    monkeypatch.setattr(cli.questionary, "select", fake_select)
    monkeypatch.setattr(cli.questionary, "text", fake_text)
    monkeypatch.setattr(cli.questionary, "confirm", fake_confirm)

    exit_code = cli.main(["--data-root", str(data_root), "--scan-roots", str(link_root)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "计划 (dry-run)" in out
    assert "完成" in out

    assert new_target.exists()
    assert (new_target / "data.txt").read_text() == "123"
    assert not target.exists()
    assert link_path.resolve() == new_target


def test_migrate_with_relative_path_resolved_against_data_root(tmp_path):
    """Test that relative paths are resolved against data_root, not cwd."""
    data_root = tmp_path / "Data"
    data_root.mkdir()

    current_target = data_root / "old"
    current_target.mkdir()
    (current_target / "file.txt").write_text("test")

    link_path = tmp_path / "link"
    link_path.symlink_to(current_target)

    # Relative path (should be resolved against data_root)
    new_target = Path("subdir/new")

    migrate_target_and_update_links(
        current_target,
        new_target,
        [link_path],
        dry_run=False,
        data_root=data_root,
    )

    expected = data_root / "subdir/new"
    assert expected.exists()
    assert (expected / "file.txt").read_text() == "test"
    assert link_path.resolve() == expected
    assert not current_target.exists()


def test_safe_move_dir_creates_parent_directories(tmp_path):
    """Test that _safe_move_dir auto-creates parent directories."""
    old = tmp_path / "old"
    old.mkdir()
    (old / "file.txt").write_text("test")

    # Parent directories don't exist
    new = tmp_path / "nonexistent" / "parent" / "new"

    _safe_move_dir(old, new)

    assert new.exists()
    assert (new / "file.txt").read_text() == "test"
    assert not old.exists()
    # Verify parent was created
    assert new.parent.exists()
    assert new.parent.parent.exists()
