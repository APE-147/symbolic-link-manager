from __future__ import annotations

from pathlib import Path
import os

from symlink_manager.core.classifier import (
    parse_markdown_config_text,
    load_markdown_config,
    classify_symlinks,
)
from symlink_manager.core.scanner import scan_symlinks


def test_parse_markdown_config_basic() -> None:
    md = """
    # Project Classification

    ## Alpha
    - alpha/**
    - common/*.lnk

    ## Beta
    - beta/*
    """.strip()

    cfg = parse_markdown_config_text(md)
    assert list(cfg.keys()) == ["Alpha", "Beta"]
    assert cfg["Alpha"] == ["alpha/**", "common/*.lnk"]
    assert cfg["Beta"] == ["beta/*"]


def test_classify_with_relative_patterns_and_first_match_wins(tmp_path: Path) -> None:
    # Layout
    # tmp/alpha/foo.ln -> tmp/target_dir
    # tmp/beta/bar.ln  -> tmp/target_dir
    # tmp/misc/zzz.ln  -> tmp/target_dir
    target = tmp_path / "target_dir"
    target.mkdir()

    (tmp_path / "alpha").mkdir()
    (tmp_path / "beta").mkdir()
    (tmp_path / "misc").mkdir()

    a = tmp_path / "alpha" / "foo.ln"
    b = tmp_path / "beta" / "bar.ln"
    z = tmp_path / "misc" / "zzz.ln"
    os.symlink(target, a)
    os.symlink(target, b)
    os.symlink(target, z)

    # Config: Beta tries to also match alpha/foo*, but Alpha's rule appears first
    md = """
    ## Alpha
    - alpha/**
    ## Beta
    - beta/**
    - alpha/foo*
    """.strip()
    cfg = parse_markdown_config_text(md)

    links = scan_symlinks(tmp_path)
    buckets = classify_symlinks(links, cfg, scan_root=tmp_path)

    # Alpha gets foo.ln due to first-match-wins
    alpha_names = {p.name for p in buckets["Alpha"]}
    assert alpha_names == {"foo.ln"}

    # Beta gets bar.ln
    beta_names = {p.name for p in buckets["Beta"]}
    assert beta_names == {"bar.ln"}

    # Unmatched goes to unclassified
    unclassified_names = {p.name for p in buckets["unclassified"]}
    assert unclassified_names == {"zzz.ln"}


def test_missing_or_invalid_config_falls_back_to_unclassified(tmp_path: Path) -> None:
    # Create a single symlink
    target = tmp_path / "t_dir"
    target.mkdir()
    link = tmp_path / "L"
    os.symlink(target, link)

    links = scan_symlinks(tmp_path)

    # No config
    cfg_empty = load_markdown_config(None)
    assert cfg_empty == {}
    buckets = classify_symlinks(links, cfg_empty, scan_root=tmp_path)
    assert {p.name for p in buckets["unclassified"]} == {"L"}

