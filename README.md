slm — Symlink Target Migrator (Questionary)

Quickstart
- `pip install -e .`
- Run `slm` (or the shorter alias `lk`) and follow the prompts (Questionary UI).

What you get
- Scans the requested roots (default `~/Developer/Cloud/Dropbox/-Code-/Scripts`) for directory symlinks whose targets live beneath the Data root (default `~/Developer/Data`).
- Groups symlinks by their resolved target so every consumer is migrated together.
- Always presents a dry-run plan and asks for confirmation before any change is made.
- Prints fast directory summaries (file count + bytes) for current and destination paths so you can spot drift.
- Retargets links as **relative symlinks by default** to make moves portable; absolute links remain available, and you can materialize data without symlinks.
- Provides `slm --relative` (or `lk --relative`) to rewrite already-detected symlinks into relative form without moving any directories.

Configuration
- Optional config file `~/.config/slm.yml` (requires PyYAML). CLI flags still override config values.
- When a config file was loaded the CLI prints `已加载配置文件：<path>` for traceability.
- Example:
  ```yaml
  data_root: /Users/username/Developer/Data
  scan_roots:
    - /Users/username
    - /Volumes/Work
  ```

Conflict handling
- If the destination already exists you pick a strategy via Questionary:
  - `中止` — keep the original layout, nothing is changed.
  - `备份后迁移` — rename the existing directory to `dest~YYYYMMDD-HHMMSS` (adds `-N` if a collision occurs) and continue.
  - Force overwrite is intentionally unsupported.
- The chosen strategy appears in the dry-run plan and, if logging is enabled, produces a `backup` record.

Logging
- Pass `--log-json out.jsonl` to append JSON Lines during both `preview` and `applied` phases.
- Each record includes `phase`, `type` (`backup`/`move`/`retarget`/`materialize`), relevant paths, `link_mode`, and a Unix timestamp float (`ts`).
- Example session:
  ```
  TMP=$(mktemp -d)
  mkdir -p "$TMP/Data/Target" "$TMP/Home"
  ln -s "$TMP/Data/Target" "$TMP/Home/my-link"

  slm --data-root "$TMP/Data" --scan-roots "$TMP/Home" \
      --log-json "$TMP/slm-actions.jsonl"

  jq . "$TMP/slm-actions.jsonl"
  jq -r '.type' "$TMP/slm-actions.jsonl"
  ```

Path resolution rules
- **Absolute paths**: `/Users/username/Developer/Data/new_target` → used as-is.
- **Home-relative paths**: `~/Developer/Data/new_target` → expanded to user's home directory.
- **Relative paths**: `dev/new_target` → resolved against `--data-root`.
  - Example: `--data-root ~/Developer/Data` + input `dev/new` → `/Users/username/Developer/Data/dev/new`
  - Parent directories are auto-created if they don't exist.
- This makes it easy to reorganize within your Data directory without typing the full path every time.

Link modes
- `--link-mode relative` (default): recreate symlinks using paths relative to where the link lives; great for portability and moving projects.
- `--link-mode absolute`: keep the previous behaviour and write absolute symlinks to the new target.
- `--link-mode inline`: do not leave symlinks behind—move the data, then materialize real directories at every former link path (creates copies when multiple links exist).
- `--relative`: standalone retarget-only mode that keeps targets in place and rewrites all discovered symlinks to relative paths under the current Data root.

CLI tips
- `--scan-roots` accepts multiple paths: `slm --scan-roots ~ ~/Developer ~/Projects` (or use `lk` as a shorter alias).
- The CLI already runs in dry-run mode by default; after previewing you confirm `执行上述操作吗？` to actually migrate.
- Passing `--dry-run` keeps backward compatibility with earlier scripts; omitting it yields the same behaviour.
- Both `slm` and `lk` commands are identical and can be used interchangeably.
- Use `slm --relative` to convert existing symlinks (found under the scan roots) into relative symlinks without moving data.

Safety
- Only directory symlinks are considered; broken or file-only links are skipped.
- Cross-device moves fall back to `shutil.copytree` + delete before relinking.
- After execution every managed symlink is re-resolved and verified to point at the new target.
