# Gitingest Digest
- Source: `/Users/ns/Developer/Cloud/Dropbox/-Code-/Scripts/service/manager/link-changer`
- Generated: 2025-11-22 13:56:53 UTC

## Summary
Directory: link-changer
Files analyzed: 22

Estimated tokens: 25.8k

## Directory Structure
```
└── link-changer/
    ├── README.md
    ├── AGENTS.md
    ├── project_settings.yaml
    ├── pyproject.toml
    ├── uv.lock
    ├── docs/
    │   ├── PLAN.md
    │   ├── REPORTS.md
    │   ├── REQUIRES.md
    │   ├── SECURITY.md
    │   ├── TASKS.md
    │   └── USAGE_EXAMPLE.md
    ├── src/
    │   └── slm/
    │       ├── __init__.py
    │       ├── cli.py
    │       ├── config.py
    │       ├── version.py
    │       ├── core/
    │       │   ├── __init__.py
    │       │   ├── migration.py
    │       │   ├── scanner.py
    │       │   └── summary.py
    │       └── services/
    │           ├── __init__.py
    │           └── configuration.py
    └── tests/
        └── test_cli.py
```

## Files
================================================
FILE: README.md
================================================
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



================================================
FILE: AGENTS.md
================================================
[Binary file]


================================================
FILE: project_settings.yaml
================================================
project:
  name: symbolic_link_changer
  slug: slm
  cycle: 1
  owner: codex
structure_contract:
  root_allowed:
    - AGENTS.md
    - README.md
    - project_settings.yaml
    - pyproject.toml
    - uv.lock
    - data/
    - docs/
    - src/
    - tests/
    - backup/
    - .env
    - .env.example
    - .gitignore
    - .specstory
    - .cursorindexingignore
    - .vscode/
  docs_core:
    - docs/REQUIRES.md
    - docs/PLAN.md
    - docs/TASKS.md
  docs_archive: backup/docs
  data_symlink: data -> /Users/niceday/Developer/Data/symbolic_link_changer-data
quality_gates:
  tests: uv run pytest tests
  lint: null
notes: |
  Aligns the project with the project-structure framework and documents the
  guaranteed root layout plus the dedicated external data directory.



================================================
FILE: pyproject.toml
================================================
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "slm"
version = "0.1.0"
description = "Questionary-based symlink target migration tool"
readme = "README.md"
requires-python = ">=3.9"
authors = [{name = "niceday"}]
dependencies = [
  "questionary>=2.0.1,<3.0",
  "PyYAML>=6.0",
]

[project.scripts]
slm = "slm.cli:main"
lk = "slm.cli:main"

[tool.setuptools]
package-dir = {"" = "src"}



================================================
FILE: uv.lock
================================================
version = 1
revision = 2
requires-python = ">=3.9"

[[package]]
name = "prompt-toolkit"
version = "3.0.52"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "wcwidth" },
]
sdist = { url = "https://files.pythonhosted.org/packages/a1/96/06e01a7b38dce6fe1db213e061a4602dd6032a8a97ef6c1a862537732421/prompt_toolkit-3.0.52.tar.gz", hash = "sha256:28cde192929c8e7321de85de1ddbe736f1375148b02f2e17edd840042b1be855", size = 434198, upload-time = "2025-08-27T15:24:02.057Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/84/03/0d3ce49e2505ae70cf43bc5bb3033955d2fc9f932163e84dc0779cc47f48/prompt_toolkit-3.0.52-py3-none-any.whl", hash = "sha256:9aac639a3bbd33284347de5ad8d68ecc044b91a762dc39b7c21095fcd6a19955", size = 391431, upload-time = "2025-08-27T15:23:59.498Z" },
]

[[package]]
name = "pyyaml"
version = "6.0.3"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz", hash = "sha256:d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f", size = 130960, upload-time = "2025-09-25T21:33:16.546Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/f4/a0/39350dd17dd6d6c6507025c0e53aef67a9293a6d37d3511f23ea510d5800/pyyaml-6.0.3-cp310-cp310-macosx_10_13_x86_64.whl", hash = "sha256:214ed4befebe12df36bcc8bc2b64b396ca31be9304b8f59e25c11cf94a4c033b", size = 184227, upload-time = "2025-09-25T21:31:46.04Z" },
    { url = "https://files.pythonhosted.org/packages/05/14/52d505b5c59ce73244f59c7a50ecf47093ce4765f116cdb98286a71eeca2/pyyaml-6.0.3-cp310-cp310-macosx_11_0_arm64.whl", hash = "sha256:02ea2dfa234451bbb8772601d7b8e426c2bfa197136796224e50e35a78777956", size = 174019, upload-time = "2025-09-25T21:31:47.706Z" },
    { url = "https://files.pythonhosted.org/packages/43/f7/0e6a5ae5599c838c696adb4e6330a59f463265bfa1e116cfd1fbb0abaaae/pyyaml-6.0.3-cp310-cp310-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:b30236e45cf30d2b8e7b3e85881719e98507abed1011bf463a8fa23e9c3e98a8", size = 740646, upload-time = "2025-09-25T21:31:49.21Z" },
    { url = "https://files.pythonhosted.org/packages/2f/3a/61b9db1d28f00f8fd0ae760459a5c4bf1b941baf714e207b6eb0657d2578/pyyaml-6.0.3-cp310-cp310-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:66291b10affd76d76f54fad28e22e51719ef9ba22b29e1d7d03d6777a9174198", size = 840793, upload-time = "2025-09-25T21:31:50.735Z" },
    { url = "https://files.pythonhosted.org/packages/7a/1e/7acc4f0e74c4b3d9531e24739e0ab832a5edf40e64fbae1a9c01941cabd7/pyyaml-6.0.3-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:9c7708761fccb9397fe64bbc0395abcae8c4bf7b0eac081e12b809bf47700d0b", size = 770293, upload-time = "2025-09-25T21:31:51.828Z" },
    { url = "https://files.pythonhosted.org/packages/8b/ef/abd085f06853af0cd59fa5f913d61a8eab65d7639ff2a658d18a25d6a89d/pyyaml-6.0.3-cp310-cp310-musllinux_1_2_aarch64.whl", hash = "sha256:418cf3f2111bc80e0933b2cd8cd04f286338bb88bdc7bc8e6dd775ebde60b5e0", size = 732872, upload-time = "2025-09-25T21:31:53.282Z" },
    { url = "https://files.pythonhosted.org/packages/1f/15/2bc9c8faf6450a8b3c9fc5448ed869c599c0a74ba2669772b1f3a0040180/pyyaml-6.0.3-cp310-cp310-musllinux_1_2_x86_64.whl", hash = "sha256:5e0b74767e5f8c593e8c9b5912019159ed0533c70051e9cce3e8b6aa699fcd69", size = 758828, upload-time = "2025-09-25T21:31:54.807Z" },
    { url = "https://files.pythonhosted.org/packages/a3/00/531e92e88c00f4333ce359e50c19b8d1de9fe8d581b1534e35ccfbc5f393/pyyaml-6.0.3-cp310-cp310-win32.whl", hash = "sha256:28c8d926f98f432f88adc23edf2e6d4921ac26fb084b028c733d01868d19007e", size = 142415, upload-time = "2025-09-25T21:31:55.885Z" },
    { url = "https://files.pythonhosted.org/packages/2a/fa/926c003379b19fca39dd4634818b00dec6c62d87faf628d1394e137354d4/pyyaml-6.0.3-cp310-cp310-win_amd64.whl", hash = "sha256:bdb2c67c6c1390b63c6ff89f210c8fd09d9a1217a465701eac7316313c915e4c", size = 158561, upload-time = "2025-09-25T21:31:57.406Z" },
    { url = "https://files.pythonhosted.org/packages/6d/16/a95b6757765b7b031c9374925bb718d55e0a9ba8a1b6a12d25962ea44347/pyyaml-6.0.3-cp311-cp311-macosx_10_13_x86_64.whl", hash = "sha256:44edc647873928551a01e7a563d7452ccdebee747728c1080d881d68af7b997e", size = 185826, upload-time = "2025-09-25T21:31:58.655Z" },
    { url = "https://files.pythonhosted.org/packages/16/19/13de8e4377ed53079ee996e1ab0a9c33ec2faf808a4647b7b4c0d46dd239/pyyaml-6.0.3-cp311-cp311-macosx_11_0_arm64.whl", hash = "sha256:652cb6edd41e718550aad172851962662ff2681490a8a711af6a4d288dd96824", size = 175577, upload-time = "2025-09-25T21:32:00.088Z" },
    { url = "https://files.pythonhosted.org/packages/0c/62/d2eb46264d4b157dae1275b573017abec435397aa59cbcdab6fc978a8af4/pyyaml-6.0.3-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:10892704fc220243f5305762e276552a0395f7beb4dbf9b14ec8fd43b57f126c", size = 775556, upload-time = "2025-09-25T21:32:01.31Z" },
    { url = "https://files.pythonhosted.org/packages/10/cb/16c3f2cf3266edd25aaa00d6c4350381c8b012ed6f5276675b9eba8d9ff4/pyyaml-6.0.3-cp311-cp311-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:850774a7879607d3a6f50d36d04f00ee69e7fc816450e5f7e58d7f17f1ae5c00", size = 882114, upload-time = "2025-09-25T21:32:03.376Z" },
    { url = "https://files.pythonhosted.org/packages/71/60/917329f640924b18ff085ab889a11c763e0b573da888e8404ff486657602/pyyaml-6.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:b8bb0864c5a28024fac8a632c443c87c5aa6f215c0b126c449ae1a150412f31d", size = 806638, upload-time = "2025-09-25T21:32:04.553Z" },
    { url = "https://files.pythonhosted.org/packages/dd/6f/529b0f316a9fd167281a6c3826b5583e6192dba792dd55e3203d3f8e655a/pyyaml-6.0.3-cp311-cp311-musllinux_1_2_aarch64.whl", hash = "sha256:1d37d57ad971609cf3c53ba6a7e365e40660e3be0e5175fa9f2365a379d6095a", size = 767463, upload-time = "2025-09-25T21:32:06.152Z" },
    { url = "https://files.pythonhosted.org/packages/f2/6a/b627b4e0c1dd03718543519ffb2f1deea4a1e6d42fbab8021936a4d22589/pyyaml-6.0.3-cp311-cp311-musllinux_1_2_x86_64.whl", hash = "sha256:37503bfbfc9d2c40b344d06b2199cf0e96e97957ab1c1b546fd4f87e53e5d3e4", size = 794986, upload-time = "2025-09-25T21:32:07.367Z" },
    { url = "https://files.pythonhosted.org/packages/45/91/47a6e1c42d9ee337c4839208f30d9f09caa9f720ec7582917b264defc875/pyyaml-6.0.3-cp311-cp311-win32.whl", hash = "sha256:8098f252adfa6c80ab48096053f512f2321f0b998f98150cea9bd23d83e1467b", size = 142543, upload-time = "2025-09-25T21:32:08.95Z" },
    { url = "https://files.pythonhosted.org/packages/da/e3/ea007450a105ae919a72393cb06f122f288ef60bba2dc64b26e2646fa315/pyyaml-6.0.3-cp311-cp311-win_amd64.whl", hash = "sha256:9f3bfb4965eb874431221a3ff3fdcddc7e74e3b07799e0e84ca4a0f867d449bf", size = 158763, upload-time = "2025-09-25T21:32:09.96Z" },
    { url = "https://files.pythonhosted.org/packages/d1/33/422b98d2195232ca1826284a76852ad5a86fe23e31b009c9886b2d0fb8b2/pyyaml-6.0.3-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:7f047e29dcae44602496db43be01ad42fc6f1cc0d8cd6c83d342306c32270196", size = 182063, upload-time = "2025-09-25T21:32:11.445Z" },
    { url = "https://files.pythonhosted.org/packages/89/a0/6cf41a19a1f2f3feab0e9c0b74134aa2ce6849093d5517a0c550fe37a648/pyyaml-6.0.3-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0", size = 173973, upload-time = "2025-09-25T21:32:12.492Z" },
    { url = "https://files.pythonhosted.org/packages/ed/23/7a778b6bd0b9a8039df8b1b1d80e2e2ad78aa04171592c8a5c43a56a6af4/pyyaml-6.0.3-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:9149cad251584d5fb4981be1ecde53a1ca46c891a79788c0df828d2f166bda28", size = 775116, upload-time = "2025-09-25T21:32:13.652Z" },
    { url = "https://files.pythonhosted.org/packages/65/30/d7353c338e12baef4ecc1b09e877c1970bd3382789c159b4f89d6a70dc09/pyyaml-6.0.3-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:5fdec68f91a0c6739b380c83b951e2c72ac0197ace422360e6d5a959d8d97b2c", size = 844011, upload-time = "2025-09-25T21:32:15.21Z" },
    { url = "https://files.pythonhosted.org/packages/8b/9d/b3589d3877982d4f2329302ef98a8026e7f4443c765c46cfecc8858c6b4b/pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc", size = 807870, upload-time = "2025-09-25T21:32:16.431Z" },
    { url = "https://files.pythonhosted.org/packages/05/c0/b3be26a015601b822b97d9149ff8cb5ead58c66f981e04fedf4e762f4bd4/pyyaml-6.0.3-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:8dc52c23056b9ddd46818a57b78404882310fb473d63f17b07d5c40421e47f8e", size = 761089, upload-time = "2025-09-25T21:32:17.56Z" },
    { url = "https://files.pythonhosted.org/packages/be/8e/98435a21d1d4b46590d5459a22d88128103f8da4c2d4cb8f14f2a96504e1/pyyaml-6.0.3-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:41715c910c881bc081f1e8872880d3c650acf13dfa8214bad49ed4cede7c34ea", size = 790181, upload-time = "2025-09-25T21:32:18.834Z" },
    { url = "https://files.pythonhosted.org/packages/74/93/7baea19427dcfbe1e5a372d81473250b379f04b1bd3c4c5ff825e2327202/pyyaml-6.0.3-cp312-cp312-win32.whl", hash = "sha256:96b533f0e99f6579b3d4d4995707cf36df9100d67e0c8303a0c55b27b5f99bc5", size = 137658, upload-time = "2025-09-25T21:32:20.209Z" },
    { url = "https://files.pythonhosted.org/packages/86/bf/899e81e4cce32febab4fb42bb97dcdf66bc135272882d1987881a4b519e9/pyyaml-6.0.3-cp312-cp312-win_amd64.whl", hash = "sha256:5fcd34e47f6e0b794d17de1b4ff496c00986e1c83f7ab2fb8fcfe9616ff7477b", size = 154003, upload-time = "2025-09-25T21:32:21.167Z" },
    { url = "https://files.pythonhosted.org/packages/1a/08/67bd04656199bbb51dbed1439b7f27601dfb576fb864099c7ef0c3e55531/pyyaml-6.0.3-cp312-cp312-win_arm64.whl", hash = "sha256:64386e5e707d03a7e172c0701abfb7e10f0fb753ee1d773128192742712a98fd", size = 140344, upload-time = "2025-09-25T21:32:22.617Z" },
    { url = "https://files.pythonhosted.org/packages/d1/11/0fd08f8192109f7169db964b5707a2f1e8b745d4e239b784a5a1dd80d1db/pyyaml-6.0.3-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:8da9669d359f02c0b91ccc01cac4a67f16afec0dac22c2ad09f46bee0697eba8", size = 181669, upload-time = "2025-09-25T21:32:23.673Z" },
    { url = "https://files.pythonhosted.org/packages/b1/16/95309993f1d3748cd644e02e38b75d50cbc0d9561d21f390a76242ce073f/pyyaml-6.0.3-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:2283a07e2c21a2aa78d9c4442724ec1eb15f5e42a723b99cb3d822d48f5f7ad1", size = 173252, upload-time = "2025-09-25T21:32:25.149Z" },
    { url = "https://files.pythonhosted.org/packages/50/31/b20f376d3f810b9b2371e72ef5adb33879b25edb7a6d072cb7ca0c486398/pyyaml-6.0.3-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:ee2922902c45ae8ccada2c5b501ab86c36525b883eff4255313a253a3160861c", size = 767081, upload-time = "2025-09-25T21:32:26.575Z" },
    { url = "https://files.pythonhosted.org/packages/49/1e/a55ca81e949270d5d4432fbbd19dfea5321eda7c41a849d443dc92fd1ff7/pyyaml-6.0.3-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:a33284e20b78bd4a18c8c2282d549d10bc8408a2a7ff57653c0cf0b9be0afce5", size = 841159, upload-time = "2025-09-25T21:32:27.727Z" },
    { url = "https://files.pythonhosted.org/packages/74/27/e5b8f34d02d9995b80abcef563ea1f8b56d20134d8f4e5e81733b1feceb2/pyyaml-6.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:0f29edc409a6392443abf94b9cf89ce99889a1dd5376d94316ae5145dfedd5d6", size = 801626, upload-time = "2025-09-25T21:32:28.878Z" },
    { url = "https://files.pythonhosted.org/packages/f9/11/ba845c23988798f40e52ba45f34849aa8a1f2d4af4b798588010792ebad6/pyyaml-6.0.3-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:f7057c9a337546edc7973c0d3ba84ddcdf0daa14533c2065749c9075001090e6", size = 753613, upload-time = "2025-09-25T21:32:30.178Z" },
    { url = "https://files.pythonhosted.org/packages/3d/e0/7966e1a7bfc0a45bf0a7fb6b98ea03fc9b8d84fa7f2229e9659680b69ee3/pyyaml-6.0.3-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:eda16858a3cab07b80edaf74336ece1f986ba330fdb8ee0d6c0d68fe82bc96be", size = 794115, upload-time = "2025-09-25T21:32:31.353Z" },
    { url = "https://files.pythonhosted.org/packages/de/94/980b50a6531b3019e45ddeada0626d45fa85cbe22300844a7983285bed3b/pyyaml-6.0.3-cp313-cp313-win32.whl", hash = "sha256:d0eae10f8159e8fdad514efdc92d74fd8d682c933a6dd088030f3834bc8e6b26", size = 137427, upload-time = "2025-09-25T21:32:32.58Z" },
    { url = "https://files.pythonhosted.org/packages/97/c9/39d5b874e8b28845e4ec2202b5da735d0199dbe5b8fb85f91398814a9a46/pyyaml-6.0.3-cp313-cp313-win_amd64.whl", hash = "sha256:79005a0d97d5ddabfeeea4cf676af11e647e41d81c9a7722a193022accdb6b7c", size = 154090, upload-time = "2025-09-25T21:32:33.659Z" },
    { url = "https://files.pythonhosted.org/packages/73/e8/2bdf3ca2090f68bb3d75b44da7bbc71843b19c9f2b9cb9b0f4ab7a5a4329/pyyaml-6.0.3-cp313-cp313-win_arm64.whl", hash = "sha256:5498cd1645aa724a7c71c8f378eb29ebe23da2fc0d7a08071d89469bf1d2defb", size = 140246, upload-time = "2025-09-25T21:32:34.663Z" },
    { url = "https://files.pythonhosted.org/packages/9d/8c/f4bd7f6465179953d3ac9bc44ac1a8a3e6122cf8ada906b4f96c60172d43/pyyaml-6.0.3-cp314-cp314-macosx_10_13_x86_64.whl", hash = "sha256:8d1fab6bb153a416f9aeb4b8763bc0f22a5586065f86f7664fc23339fc1c1fac", size = 181814, upload-time = "2025-09-25T21:32:35.712Z" },
    { url = "https://files.pythonhosted.org/packages/bd/9c/4d95bb87eb2063d20db7b60faa3840c1b18025517ae857371c4dd55a6b3a/pyyaml-6.0.3-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:34d5fcd24b8445fadc33f9cf348c1047101756fd760b4dacb5c3e99755703310", size = 173809, upload-time = "2025-09-25T21:32:36.789Z" },
    { url = "https://files.pythonhosted.org/packages/92/b5/47e807c2623074914e29dabd16cbbdd4bf5e9b2db9f8090fa64411fc5382/pyyaml-6.0.3-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:501a031947e3a9025ed4405a168e6ef5ae3126c59f90ce0cd6f2bfc477be31b7", size = 766454, upload-time = "2025-09-25T21:32:37.966Z" },
    { url = "https://files.pythonhosted.org/packages/02/9e/e5e9b168be58564121efb3de6859c452fccde0ab093d8438905899a3a483/pyyaml-6.0.3-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:b3bc83488de33889877a0f2543ade9f70c67d66d9ebb4ac959502e12de895788", size = 836355, upload-time = "2025-09-25T21:32:39.178Z" },
    { url = "https://files.pythonhosted.org/packages/88/f9/16491d7ed2a919954993e48aa941b200f38040928474c9e85ea9e64222c3/pyyaml-6.0.3-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:c458b6d084f9b935061bc36216e8a69a7e293a2f1e68bf956dcd9e6cbcd143f5", size = 794175, upload-time = "2025-09-25T21:32:40.865Z" },
    { url = "https://files.pythonhosted.org/packages/dd/3f/5989debef34dc6397317802b527dbbafb2b4760878a53d4166579111411e/pyyaml-6.0.3-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:7c6610def4f163542a622a73fb39f534f8c101d690126992300bf3207eab9764", size = 755228, upload-time = "2025-09-25T21:32:42.084Z" },
    { url = "https://files.pythonhosted.org/packages/d7/ce/af88a49043cd2e265be63d083fc75b27b6ed062f5f9fd6cdc223ad62f03e/pyyaml-6.0.3-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:5190d403f121660ce8d1d2c1bb2ef1bd05b5f68533fc5c2ea899bd15f4399b35", size = 789194, upload-time = "2025-09-25T21:32:43.362Z" },
    { url = "https://files.pythonhosted.org/packages/23/20/bb6982b26a40bb43951265ba29d4c246ef0ff59c9fdcdf0ed04e0687de4d/pyyaml-6.0.3-cp314-cp314-win_amd64.whl", hash = "sha256:4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac", size = 156429, upload-time = "2025-09-25T21:32:57.844Z" },
    { url = "https://files.pythonhosted.org/packages/f4/f4/a4541072bb9422c8a883ab55255f918fa378ecf083f5b85e87fc2b4eda1b/pyyaml-6.0.3-cp314-cp314-win_arm64.whl", hash = "sha256:93dda82c9c22deb0a405ea4dc5f2d0cda384168e466364dec6255b293923b2f3", size = 143912, upload-time = "2025-09-25T21:32:59.247Z" },
    { url = "https://files.pythonhosted.org/packages/7c/f9/07dd09ae774e4616edf6cda684ee78f97777bdd15847253637a6f052a62f/pyyaml-6.0.3-cp314-cp314t-macosx_10_13_x86_64.whl", hash = "sha256:02893d100e99e03eda1c8fd5c441d8c60103fd175728e23e431db1b589cf5ab3", size = 189108, upload-time = "2025-09-25T21:32:44.377Z" },
    { url = "https://files.pythonhosted.org/packages/4e/78/8d08c9fb7ce09ad8c38ad533c1191cf27f7ae1effe5bb9400a46d9437fcf/pyyaml-6.0.3-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:c1ff362665ae507275af2853520967820d9124984e0f7466736aea23d8611fba", size = 183641, upload-time = "2025-09-25T21:32:45.407Z" },
    { url = "https://files.pythonhosted.org/packages/7b/5b/3babb19104a46945cf816d047db2788bcaf8c94527a805610b0289a01c6b/pyyaml-6.0.3-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:6adc77889b628398debc7b65c073bcb99c4a0237b248cacaf3fe8a557563ef6c", size = 831901, upload-time = "2025-09-25T21:32:48.83Z" },
    { url = "https://files.pythonhosted.org/packages/8b/cc/dff0684d8dc44da4d22a13f35f073d558c268780ce3c6ba1b87055bb0b87/pyyaml-6.0.3-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:a80cb027f6b349846a3bf6d73b5e95e782175e52f22108cfa17876aaeff93702", size = 861132, upload-time = "2025-09-25T21:32:50.149Z" },
    { url = "https://files.pythonhosted.org/packages/b1/5e/f77dc6b9036943e285ba76b49e118d9ea929885becb0a29ba8a7c75e29fe/pyyaml-6.0.3-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:00c4bdeba853cc34e7dd471f16b4114f4162dc03e6b7afcc2128711f0eca823c", size = 839261, upload-time = "2025-09-25T21:32:51.808Z" },
    { url = "https://files.pythonhosted.org/packages/ce/88/a9db1376aa2a228197c58b37302f284b5617f56a5d959fd1763fb1675ce6/pyyaml-6.0.3-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:66e1674c3ef6f541c35191caae2d429b967b99e02040f5ba928632d9a7f0f065", size = 805272, upload-time = "2025-09-25T21:32:52.941Z" },
    { url = "https://files.pythonhosted.org/packages/da/92/1446574745d74df0c92e6aa4a7b0b3130706a4142b2d1a5869f2eaa423c6/pyyaml-6.0.3-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:16249ee61e95f858e83976573de0f5b2893b3677ba71c9dd36b9cf8be9ac6d65", size = 829923, upload-time = "2025-09-25T21:32:54.537Z" },
    { url = "https://files.pythonhosted.org/packages/f0/7a/1c7270340330e575b92f397352af856a8c06f230aa3e76f86b39d01b416a/pyyaml-6.0.3-cp314-cp314t-win_amd64.whl", hash = "sha256:4ad1906908f2f5ae4e5a8ddfce73c320c2a1429ec52eafd27138b7f1cbe341c9", size = 174062, upload-time = "2025-09-25T21:32:55.767Z" },
    { url = "https://files.pythonhosted.org/packages/f1/12/de94a39c2ef588c7e6455cfbe7343d3b2dc9d6b6b2f40c4c6565744c873d/pyyaml-6.0.3-cp314-cp314t-win_arm64.whl", hash = "sha256:ebc55a14a21cb14062aa4162f906cd962b28e2e9ea38f9b4391244cd8de4ae0b", size = 149341, upload-time = "2025-09-25T21:32:56.828Z" },
    { url = "https://files.pythonhosted.org/packages/9f/62/67fc8e68a75f738c9200422bf65693fb79a4cd0dc5b23310e5202e978090/pyyaml-6.0.3-cp39-cp39-macosx_10_13_x86_64.whl", hash = "sha256:b865addae83924361678b652338317d1bd7e79b1f4596f96b96c77a5a34b34da", size = 184450, upload-time = "2025-09-25T21:33:00.618Z" },
    { url = "https://files.pythonhosted.org/packages/ae/92/861f152ce87c452b11b9d0977952259aa7df792d71c1053365cc7b09cc08/pyyaml-6.0.3-cp39-cp39-macosx_11_0_arm64.whl", hash = "sha256:c3355370a2c156cffb25e876646f149d5d68f5e0a3ce86a5084dd0b64a994917", size = 174319, upload-time = "2025-09-25T21:33:02.086Z" },
    { url = "https://files.pythonhosted.org/packages/d0/cd/f0cfc8c74f8a030017a2b9c771b7f47e5dd702c3e28e5b2071374bda2948/pyyaml-6.0.3-cp39-cp39-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:3c5677e12444c15717b902a5798264fa7909e41153cdf9ef7ad571b704a63dd9", size = 737631, upload-time = "2025-09-25T21:33:03.25Z" },
    { url = "https://files.pythonhosted.org/packages/ef/b2/18f2bd28cd2055a79a46c9b0895c0b3d987ce40ee471cecf58a1a0199805/pyyaml-6.0.3-cp39-cp39-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:5ed875a24292240029e4483f9d4a4b8a1ae08843b9c54f43fcc11e404532a8a5", size = 836795, upload-time = "2025-09-25T21:33:05.014Z" },
    { url = "https://files.pythonhosted.org/packages/73/b9/793686b2d54b531203c160ef12bec60228a0109c79bae6c1277961026770/pyyaml-6.0.3-cp39-cp39-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:0150219816b6a1fa26fb4699fb7daa9caf09eb1999f3b70fb6e786805e80375a", size = 750767, upload-time = "2025-09-25T21:33:06.398Z" },
    { url = "https://files.pythonhosted.org/packages/a9/86/a137b39a611def2ed78b0e66ce2fe13ee701a07c07aebe55c340ed2a050e/pyyaml-6.0.3-cp39-cp39-musllinux_1_2_aarch64.whl", hash = "sha256:fa160448684b4e94d80416c0fa4aac48967a969efe22931448d853ada8baf926", size = 727982, upload-time = "2025-09-25T21:33:08.708Z" },
    { url = "https://files.pythonhosted.org/packages/dd/62/71c27c94f457cf4418ef8ccc71735324c549f7e3ea9d34aba50874563561/pyyaml-6.0.3-cp39-cp39-musllinux_1_2_x86_64.whl", hash = "sha256:27c0abcb4a5dac13684a37f76e701e054692a9b2d3064b70f5e4eb54810553d7", size = 755677, upload-time = "2025-09-25T21:33:09.876Z" },
    { url = "https://files.pythonhosted.org/packages/29/3d/6f5e0d58bd924fb0d06c3a6bad00effbdae2de5adb5cda5648006ffbd8d3/pyyaml-6.0.3-cp39-cp39-win32.whl", hash = "sha256:1ebe39cb5fc479422b83de611d14e2c0d3bb2a18bbcb01f229ab3cfbd8fee7a0", size = 142592, upload-time = "2025-09-25T21:33:10.983Z" },
    { url = "https://files.pythonhosted.org/packages/f0/0c/25113e0b5e103d7f1490c0e947e303fe4a696c10b501dea7a9f49d4e876c/pyyaml-6.0.3-cp39-cp39-win_amd64.whl", hash = "sha256:2e71d11abed7344e42a8849600193d15b6def118602c4c176f748e4583246007", size = 158777, upload-time = "2025-09-25T21:33:15.55Z" },
]

[[package]]
name = "questionary"
version = "2.1.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "prompt-toolkit" },
]
sdist = { url = "https://files.pythonhosted.org/packages/f6/45/eafb0bba0f9988f6a2520f9ca2df2c82ddfa8d67c95d6625452e97b204a5/questionary-2.1.1.tar.gz", hash = "sha256:3d7e980292bb0107abaa79c68dd3eee3c561b83a0f89ae482860b181c8bd412d", size = 25845, upload-time = "2025-08-28T19:00:20.851Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/3c/26/1062c7ec1b053db9e499b4d2d5bc231743201b74051c973dadeac80a8f43/questionary-2.1.1-py3-none-any.whl", hash = "sha256:a51af13f345f1cdea62347589fbb6df3b290306ab8930713bfae4d475a7d4a59", size = 36753, upload-time = "2025-08-28T19:00:19.56Z" },
]

[[package]]
name = "slm"
version = "0.1.0"
source = { editable = "." }
dependencies = [
    { name = "pyyaml" },
    { name = "questionary" },
]

[package.metadata]
requires-dist = [
    { name = "pyyaml", specifier = ">=6.0" },
    { name = "questionary", specifier = ">=2.0.1,<3.0" },
]

[[package]]
name = "wcwidth"
version = "0.2.14"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/24/30/6b0809f4510673dc723187aeaf24c7f5459922d01e2f794277a3dfb90345/wcwidth-0.2.14.tar.gz", hash = "sha256:4d478375d31bc5395a3c55c40ccdf3354688364cd61c4f6adacaa9215d0b3605", size = 102293, upload-time = "2025-09-22T16:29:53.023Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/af/b5/123f13c975e9f27ab9c0770f514345bd406d0e8d3b7a0723af9d43f710af/wcwidth-0.2.14-py2.py3-none-any.whl", hash = "sha256:a7bb560c8aee30f9957e5f9895805edd20602f2d7f720186dfd906e82b4982e1", size = 37286, upload-time = "2025-09-22T16:29:51.641Z" },
]



================================================
FILE: docs/PLAN.md
================================================
[Binary file]


================================================
FILE: docs/REPORTS.md
================================================
[Binary file]


================================================
FILE: docs/REQUIRES.md
================================================
[Binary file]


================================================
FILE: docs/SECURITY.md
================================================
# Security & Privacy Report

## Date: 2025-10-19

## Summary
This document provides evidence of security hardening and privacy protection measures applied to the symbolic-link-manager project.

## Privacy Sanitization

### 1. Environment Variable Integration
**Implemented**: Python-dotenv support for centralized configuration
- Added `SLM_DATA_ROOT` and `SLM_SCAN_ROOTS` environment variables
- Created `.env.example` with placeholder values only
- Configuration precedence: CLI > ENV > YAML config > built-in defaults

**Files Modified**:
- `pyproject.toml`: Added python-dotenv>=1.0.0 dependency
- `src/slm/config.py`: Added `load_dotenv_if_present()`, `get_env_overrides()`, `resolve_settings()`
- `src/slm/cli.py`: Integrated environment variable resolution
- `.env.example`: Created with generic placeholders

**Verification**:
```bash
# No .env file committed
$ git ls-files | grep "^\.env$"
# (returns nothing)

# .env.example exists with placeholders only
$ cat .env.example
## Example environment configuration for lk/slm
# Copy to `.env` and adjust values as needed. Do NOT commit your real .env.
...
```

### 2. Documentation Sanitization
**Action**: Replaced all instances of real username `/Users/niceday/` with generic placeholder `/Users/username/`

**Files Cleaned**:
- README.md
- docs/USAGE_EXAMPLE.md
- docs/PLAN.md
- docs/REQUIRES.md
- docs/TASKS.md

**Command Used**:
```bash
find . -type f \( -name "*.md" -o -name "*.yml" \) \
  -not -path "./.git/*" -not -path "./backup/*" \
  -exec sed -i '' 's|/Users/niceday/|/Users/username/|g' {} \;
```

**Verification**:
```bash
$ rg "/Users/niceday" --glob="!backup/**" --glob="!.git/**"
# (returns no matches in active project files)
```

### 3. Git History Sanitization
**Tool Used**: `git-filter-repo`

**Command**:
```bash
git filter-repo --replace-text <(echo '/Users/niceday==>/Users/username') --force
```

**Result**:
```
Parsed 39 commits
New history written in 0.10 seconds
Repacking completed in 0.30 seconds
✓ Git remote 'origin' removed (expected behavior)
✓ All refs rewritten
```

**Verification**:
```bash
# Reduced occurrences - remaining are in binary .pyc content (not critical)
$ git log --all --source --full-history -S "/Users/niceday" | wc -l
3  # Only legacy binary files, no sensitive text
```

## .gitignore Hardening

### Patterns Added/Verified:
**Environment Files**:
- `.env`
- `.env.*`
- `.venv`, `venv/`, `ENV/`

**Security-Sensitive Files**:
- `*.pem`, `*.key`
- `id_rsa`, `id_rsa.*`
- `*.p12`, `*.pfx`, `*.jks`, `*.keystore`
- `*.gpg`, `*.asc`
- `secrets.*`
- `*.crt`, `*.der`, `*.kdbx`

**Data & Artifacts**:
- `data/` (symbolic link to local absolute path)
- `*.sqlite`, `*.db`, `*.mdb`
- `dumps/`, `backups/`, `exports/`

**Verification**:
```bash
$ cat .gitignore | grep -E "(\.env|\.pem|\.key|id_rsa|secrets)"
.env
.env.*
*.pem
*.key
id_rsa
id_rsa.*
secrets.*
```

## Pre-commit Hook (Planned)
**Status**: Documented in roadmap
**Recommendation**: Install lightweight pre-commit hook to block accidental commits of:
- `.env*` files
- Common secret patterns (AKIA*, ghp_*, xox*, etc.)
- Private key headers

**Implementation** (future):
```bash
# Install hook
cp .githooks/pre-commit .git/hooks/
# Or configure hooks path
git config core.hooksPath .githooks
```

## GitHub Repository Upload

### Repository Details:
- **Name**: `symbolic-link-manager`
- **Visibility**: Private
- **URL**: https://github.com/APE-147/symbolic-link-manager
- **Description**: "A Python CLI tool for managing symbolic link targets with interactive menus (Questionary). Supports safe directory migration, cross-device moves, and conflict resolution."

### Upload Actions:
```bash
# Create private repository
gh repo create "symbolic-link-manager" --private --source=. --remote=origin --push --disable-wiki

# Push all branches
git push origin --all

# Push all tags
git push origin --tags
```

### Verification:
```bash
$ gh repo view APE-147/symbolic-link-manager --json visibility,isPrivate
{
  "isPrivate": true,
  "visibility": "PRIVATE"
}
```

## Testing

### Test Results:
```bash
$ pytest tests/ -v
========================= 16 passed in 0.13s =========================
```

**Coverage**:
- Environment variable override logic
- Relative path resolution
- Argument parsing with defaults
- Migration with conflict strategies
- All existing functionality preserved

## Security Checklist

- [x] `.env` excluded from Git
- [x] `.env.example` created with placeholders only
- [x] Documentation sanitized (no real usernames/paths)
- [x] Git history rewritten to remove sensitive data
- [x] `.gitignore` hardened with comprehensive patterns
- [x] GitHub repository created as **private**
- [x] All branches and tags pushed
- [x] Tests passing (16/16)
- [x] No behavior changes (backward compatible)
- [ ] Pre-commit hooks (future enhancement)
- [ ] Dependency vulnerability scan (future enhancement)

## Recommendations

1. **Periodic Audits**: Run `git log --all -S 'pattern'` quarterly to check for accidental commits
2. **Secret Scanning**: Consider integrating GitHub's secret scanning alerts
3. **Dependency Updates**: Monitor python-dotenv, questionary, and PyYAML for security patches
4. **Access Control**: Maintain private repository status until ready for public release

## Sign-off

Date: 2025-10-19
Status: ✅ All critical privacy measures implemented
Next Review: 2025-11-19 (30 days)



================================================
FILE: docs/TASKS.md
================================================
[Binary file]


================================================
FILE: docs/USAGE_EXAMPLE.md
================================================
# slm 使用示例

## 快速开始

### 1. 安装

```bash
cd /Users/username/Developer/Cloud/Dropbox/-Code-/Scripts/system/data-storage/symbolic_link_changer
pip install -e .
```

### 2. 基本使用

#### 交互式选单（默认 dry-run + 结果确认）

```bash
slm  # 或使用更短的别名: lk
```

默认行为：
- Data root: `~/Developer/Data`
- Scan roots: `~/Developer/Cloud/Dropbox/-Code-/Scripts`（可通过配置或 CLI 覆盖）
- Dry-run: 开启。CLI 会先展示迁移计划并在 `执行上述操作吗？` 时再次确认。
- 链接模式：`relative`（默认创建相对路径符号链接，便于迁移）
- 可选模式：`slm --relative` 用于“只改写为相对链接且不移动目录”。

#### 自定义扫描范围

```bash
slm --data-root ~/Developer/Data --scan-roots ~ ~/Projects ~/Documents
```

#### 带 JSON 日志

```bash
slm --log-json ./migration.jsonl
```

查看 JSON 日志：
```bash
jq . migration.jsonl
```

#### 使用配置文件设置默认值

在 `~/.config/slm.yml` 中声明默认的 Data root 与扫描范围（需要 PyYAML）：

```yaml
data_root: /Users/username/Developer/Data
scan_roots:
  - /Users/username
  - /Users/username/Developer
```

当配置文件被加载时，CLI 会输出 `已加载配置文件：<绝对路径>`，以便追踪默认来源。CLI 参数始终优先于配置文件。

## 使用场景示例

### 场景 1：整理开发项目的 Data 目录

**背景**：你在 `~/Developer/Data` 下有多个项目的数据文件夹，其他位置的符号链接指向这些文件夹。

**步骤**：

1. 启动工具：
```bash
slm --data-root ~/Developer/Data --scan-roots ~ ~/Developer
```

2. 工具会扫描并显示所有被符号链接指向的文件夹，例如：
```
选择一个被指向的目标文件夹:
> myproject-data  (2 个链接)
  another-project-data  (1 个链接)
  退出
```

3. 选择要移动的文件夹，工具会显示所有指向它的符号链接：
```
以下符号链接指向该目录:
- /Users/username/workspace/myproject/data
- /Users/username/Documents/backup/myproject-link
```

4. 输入新的目标路径（支持 tab 自动补全）：

**使用绝对路径**：
```
输入新的目标绝对路径: /Users/username/Developer/Data/archived/myproject-data
```

**使用相对路径**（相对于 `--data-root`，更简洁）：
```
输入新的目标绝对路径: archived/myproject-data
```
相对路径会自动解析为 `~/Developer/Data/archived/myproject-data`，父目录会自动创建。

5. 如果新目标已存在，CLI 会提示冲突策略：
```
目标路径已存在：/Users/username/Developer/Data/archived/myproject-data
选择冲突处理策略：
  ◯ 中止（默认，保持现状）
  ◉ 备份后迁移（先重命名为 archived/myproject-data~20251018-193011）
  ◯ 强制覆盖（不支持）
```
选择“备份后迁移”会在执行前把既有目录重命名为 `dest~YYYYMMDD-HHMMSS`（若冲突再追加 `-N`）。

6. 确认 dry-run 计划：
```
计划 (dry-run):
  • Backup: /Users/username/Developer/Data/archived/myproject-data -> /Users/username/Developer/Data/archived/myproject-data~20251018-193011
  • Move: /Users/username/Developer/Data/myproject-data -> /Users/username/Developer/Data/archived/myproject-data
  • Link: /Users/username/workspace/myproject/data -> /Users/username/Developer/Data/archived/myproject-data
  • Link: /Users/username/Documents/backup/myproject-link -> /Users/username/Developer/Data/archived/myproject-data
summary(current=files:42 bytes:1048576, new=files:12 bytes:4096)
执行上述操作吗？ (y/N):
```

7. 确认后执行，工具会：
   - 根据冲突策略备份（如选择）
   - 移动目录到新位置（跨卷自动回退到 copytree + 删除）
  - 更新所有符号链接指向新位置
  - 验证符号链接（`Path.resolve(strict=True)` 必须指向新目标）
  - 显示最终摘要 `summary(new=files:… bytes:…)`

**链接模式提示**：
- 相对链接（默认）：无需额外参数，所有新链接写为相对路径。
- 绝对链接：添加 `--link-mode absolute`。
- 回收/不使用符号链接：`--link-mode inline` 会在迁移后删除符号链接并在原位置落盘真实目录（多处链接时会产生拷贝）。

### 场景 2：使用 JSON 日志跟踪操作

```bash
slm --log-json ./slm-operations.jsonl
```

查看操作记录：
```bash
# 查看所有操作
jq . ./slm-operations.jsonl

# 仅查看 preview 阶段
jq 'select(.phase == "preview")' ./slm-operations.jsonl

# 仅查看实际执行的移动操作
jq 'select(.phase == "applied" and .type == "move")' ./slm-operations.jsonl
```

JSON 日志格式示例（`ts` 为 Unix 时间戳浮点数）：
```json
{"phase": "preview", "type": "backup", "from": "/path/new", "to": "/path/new~20251018-120001", "ts": 1734559201.123}
{"phase": "preview", "type": "move", "from": "/path/old", "to": "/path/new", "ts": 1734559201.123}
{"phase": "preview", "type": "retarget", "link": "/workspace/link1", "to": "/path/new", "ts": 1734559201.123}
{"phase": "applied", "type": "move", "from": "/path/old", "to": "/path/new", "ts": 1734559234.987}
{"phase": "applied", "type": "retarget", "link": "/workspace/link1", "to": "/path/new", "ts": 1734559234.987}
```
*使用 `--link-mode inline` 时，`type` 会改为 `materialize` 以反映“落盘真实目录”的操作。*

### 场景 3：仅将绝对符号链接改写为相对路径

**需求**：不移动目录，仅把扫描到的符号链接改成相对路径，方便项目复制/迁移。

```bash
slm --relative
# 或 lk --relative
```

行为：
- 按默认/指定 scan roots 扫描所有指向 Data 目录的符号链接。
- 展示 dry-run 计划后确认（默认 dry-run 开启）。
- 将所有相关链接改写为相对路径，目录位置保持不变。
- 可搭配 `--log-json` 记录 retarget 操作，`link_mode` 会显示为 `relative-only`。

## 命令行选项

``` 
slm [选项]   # 或使用别名: lk [选项]

选项:
  --data-root PATH       Data 目录的根路径（默认: ~/Developer/Data）
  --scan-roots PATH ...  扫描符号链接的根目录列表（默认: ~/Developer/Cloud/Dropbox/-Code-/Scripts）
  --link-mode MODE       链接模式: relative (默认) | absolute | inline（不使用符号链接）
  --relative             仅改写为相对符号链接，不移动目标目录
  --dry-run              仅预览迁移计划（默认开启，用于兼容旧脚本）
  --log-json PATH        记录操作日志到 JSON Lines 文件
  -h, --help             显示帮助信息

注：slm 和 lk 完全等价，可互换使用。
```

## 安全特性

1. **默认 Dry-run**：所有操作需要用户确认后才会执行。
2. **仅处理目录型符号链接**：忽略文件符号链接与损坏链接。
3. **跨卷安全移动**：自动检测跨卷错误并回退到 `copytree` + 删除。
4. **移动后验证**：确保所有符号链接 `resolve()` 到新的目标。
5. **排除噪音目录**：自动跳过 `.git`, `Library`, `.cache`, `node_modules`, `.venv`, `venv` 等常见目录。

## 目录树摘要说明

工具会显示两种摘要：

1. **Dry-run 预览摘要**：
   ```
   summary(current=files:42 bytes:1048576, new=files:12 bytes:4096)
   ```
   - `current`: 当前目标目录的文件统计
   - `new`: 新目标位置的文件统计（如不存在则为 0）

2. **执行后最终摘要**：
   ```
   summary(new=files:42 bytes:1048576)
   ```
   - 显示迁移完成后的最终状态

## 故障排查

### 问题：未找到任何符号链接

**原因**：
- 扫描范围可能不包含符号链接所在目录
- 符号链接可能指向 Data root 之外的位置

**解决方案**：
```bash
# 扩大扫描范围
slm --scan-roots ~ ~/Developer ~/Documents ~/Projects
```

### 问题：目标已存在

**当前行为**：
- 默认中止操作并提示冲突
- 可选择备份策略，将已有目标重命名为 `dest~YYYYMMDD-HHMMSS` 后继续迁移
- 强制覆盖暂不支持

### 问题：权限不足

**解决方案**：
- 确保对源目录和目标目录有读写权限
- 必要时使用 `sudo`（不推荐）

## 开发状态

当前进度：9/9 任务完成（100%）。

已完成：
- ✅ 项目初始化与依赖
- ✅ 符号链接发现器
- ✅ Questionary 多级菜单
- ✅ 迁移执行器（含跨卷回退）
- ✅ JSON 日志与树摘要
- ✅ 冲突与权限处理（备份策略）
- ✅ 配置文件支持（PyYAML）
- ✅ 测试套件（4/4 通过）
- ✅ 文档与示例更新（README、USAGE、配置说明）

## 反馈与贡献

如有问题或建议，请在项目仓库提交 Issue。



================================================
FILE: src/slm/__init__.py
================================================
from .cli import main
from .version import __version__, get_version

__all__ = ["__version__", "get_version", "main"]



================================================
FILE: src/slm/cli.py
================================================
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import questionary
except Exception:  # pragma: no cover
    questionary = None

from .config import (
    ConfigError,
    LoadedConfig,
    coerce_scan_roots,
    load_config,
)
from .core import (
    MigrationError,
    _derive_backup_path,
    _safe_move_dir,
    fast_tree_summary,
    format_summary_pair,
    group_by_target_within_data,
    migrate_target_and_update_links,
    rewrite_links_to_relative,
    SymlinkInfo,
    scan_symlinks_pointing_into_data,
)

def _parse_args(argv):
    p = argparse.ArgumentParser(
        prog="slm",
        description="符号链接目标迁移（Questionary 交互界面）",
    )
    p.add_argument(
        "--data-root",
        default=None,
        help="Data directory containing real folders (default: ~/Developer/Data)",
    )
    p.add_argument(
        "--scan-roots",
        nargs="*",
        default=None,
        help="Roots to scan for symlink sources (default: ~/Developer/Cloud/Dropbox/-Code-/Scripts)",
    )
    p.add_argument(
        "--link-mode",
        choices=["relative", "absolute", "inline"],
        default="relative",
        help="How to handle links: relative symlinks (default), absolute symlinks, or inline without symlinks",
    )
    p.add_argument(
        "--relative",
        action="store_true",
        help="Rewrite found symlinks to relative paths without moving their targets",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview actions without making changes",
    )
    p.add_argument(
        "--log-json",
        dest="log_json",
        default=None,
        help="Append JSON Lines records of planned/applied actions to the given file",
    )
    return p.parse_args(argv)


def _append_json_log(
    path: Path,
    phase: str,
    current_target: Path,
    new_target: Path,
    links: Iterable[Path],
    backup_entry: Optional[Tuple[Path, Path]] = None,
    link_mode: str = "relative",
) -> None:
    """Append action records as JSON Lines.

    Each line is an object with keys: phase, type, from/to or link/to, ts.
    """
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.time()
    records = []
    if backup_entry:
        records.append(
            {
                "phase": phase,
                "type": "backup",
                "from": str(backup_entry[0]),
                "to": str(backup_entry[1]),
                "ts": ts,
            }
        )
    records.append(
        {
            "phase": phase,
            "type": "move",
            "from": str(current_target),
            "to": str(new_target),
            "link_mode": link_mode,
            "ts": ts,
        }
    )
    record_type = "materialize" if link_mode == "inline" else "retarget"
    for link in links:
        records.append(
            {
                "phase": phase,
                "type": record_type,
                "link": str(link),
                "to": str(new_target),
                "link_mode": link_mode,
                "ts": ts,
            }
        )
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _append_relative_only_log(
    path: Path, phase: str, infos: Iterable[SymlinkInfo]
) -> None:
    """Append retarget-only action records as JSON Lines."""

    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.time()
    records = []
    for info in infos:
        records.append(
            {
                "phase": phase,
                "type": "retarget",
                "link": str(info.source),
                "to": str(info.target),
                "link_mode": "relative-only",
                "ts": ts,
            }
        )
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main(argv=None):
    default_data_root = Path.home() / "Developer" / "Data"
    default_scan_roots = [
        str(Path.home() / "Developer" / "Cloud" / "Dropbox" / "-Code-" / "Scripts")
    ]
    argv = sys.argv[1:] if argv is None else argv
    args = _parse_args(argv)

    if questionary is None:
        print("未安装 questionary，请先安装依赖。")
        return 2

    try:
        loaded_config: LoadedConfig = load_config()
    except ConfigError as exc:
        print(f"配置错误：{exc}")
        return 2

    config_data: Dict[str, Any] = loaded_config.data

    if args.data_root is not None:
        data_root_str = args.data_root
    else:
        data_root_str = config_data.get("data_root", None)
    if data_root_str is None:
        data_root_str = str(default_data_root)
    if not isinstance(data_root_str, str):
        print("配置错误：data_root 必须是字符串。")
        return 2
    data_root = Path(data_root_str).expanduser().resolve()

    if args.scan_roots is not None:
        scan_roots_raw = args.scan_roots
    else:
        try:
            scan_roots_raw = coerce_scan_roots(
                config_data.get("scan_roots"),
                context=str(loaded_config.path) if loaded_config.path else "配置文件",
            )
        except ConfigError as exc:
            print(f"配置错误：{exc}")
            return 2
        if not scan_roots_raw:
            scan_roots_raw = default_scan_roots

    scan_roots = [Path(p).expanduser() for p in scan_roots_raw]

    if loaded_config.path:
        print(f"已加载配置文件：{loaded_config.path}")

    print(
        f"SLM 已准备。Data 根：{data_root} | Dry-run：{args.dry_run} | 链接模式：{args.link_mode}"
    )

    infos = scan_symlinks_pointing_into_data(scan_roots, data_root)

    if args.relative:
        if not infos:
            print("未找到指向 Data 目录的符号链接。请检查扫描范围或目录。")
            return 0
        plan = rewrite_links_to_relative(infos, dry_run=args.dry_run)
        print("计划 (relative-only):")
        for line in plan:
            print(f"  • {line}")
        if args.log_json:
            _append_relative_only_log(args.log_json, "preview", infos)
        if args.dry_run:
            proceed = questionary.confirm(
                "执行上述操作（仅改写为相对路径）吗？", default=False
            ).ask()
            if not proceed:
                print("已取消。")
                return 0
        try:
            rewrite_links_to_relative(infos, dry_run=False)
        except MigrationError as exc:
            print(f"执行失败：{exc}")
            return 2
        if args.log_json:
            _append_relative_only_log(args.log_json, "applied", infos)
        print("完成。已将符号链接改写为相对路径（未移动目录）。")
        return 0

    grouped = group_by_target_within_data(infos, data_root)

    if not grouped:
        print("未找到指向 Data 目录的符号链接。请检查扫描范围或目录。")
        return 0

    def _fmt_target(t: Path, count: int) -> str:
        try:
            rel = t.relative_to(data_root)
        except ValueError:
            rel = t
        return f"{rel}  ({count} 个链接)"

    choices = [
        questionary.Choice(title=_fmt_target(t, len(links)), value=t)
        for t, links in grouped.items()
    ]
    choices.append(questionary.Choice(title="退出", value=None))

    selected_target = questionary.select(
        "选择一个被指向的目标文件夹:", choices=choices
    ).ask()

    # Graceful exit handling across Questionary versions:
    # - Expected: our "退出" choice returns value=None
    # - Some environments may return the label string (e.g., "退出")
    # - Also handle unexpected values not present in grouped keys
    if selected_target is None or selected_target not in grouped:
        print("已取消。")
        return 0

    links = [info.source for info in grouped[selected_target]]
    display_links = "\n".join(f"- {p}" for p in links)
    print(f"以下符号链接指向该目录:\n{display_links}")

    default_new = str(selected_target)
    new_path_str = questionary.text(
        "输入新的目标绝对路径:", default=default_new
    ).ask()
    if not new_path_str:
        print("未输入新路径，已取消。")
        return 0

    new_target = Path(new_path_str).expanduser()

    conflict_strategy = "abort"
    backup_path: Optional[Path] = None
    if new_target.exists():
        print(f"目标路径已存在：{new_target}")
        backup_candidate = _derive_backup_path(new_target)
        strategy_choice = questionary.select(
            "选择冲突处理策略：",
            choices=[
                questionary.Choice(title="中止（默认，保持现状）", value="abort"),
                questionary.Choice(
                    title=f"备份后迁移（先重命名为 {backup_candidate.name}）", value="backup"
                ),
                questionary.Choice(title="强制覆盖（不支持）", value="reject"),
            ],
            default="abort",
        ).ask()
        if strategy_choice == "reject":
            print("强制覆盖暂不支持，已中止。")
            return 0
        if strategy_choice == "abort" or strategy_choice is None:
            print("已中止迁移。")
            return 0
        conflict_strategy = "backup"
        backup_path = backup_candidate

    try:
        plan = migrate_target_and_update_links(
            selected_target,
            new_target,
            links,
            dry_run=args.dry_run,
            conflict_strategy=conflict_strategy,
            backup_path=backup_path,
            data_root=data_root,
            link_mode=args.link_mode,
        )
    except MigrationError as e:
        print(f"校验失败：{e}")
        return 2

    if args.dry_run:
        print("计划 (dry-run):")
        for line in plan:
            print(f"  • {line}")
        # Fast tree summaries for preview
        curr_summary = fast_tree_summary(selected_target)
        new_summary = fast_tree_summary(new_target) if new_target.exists() else (0, 0)
        print(format_summary_pair(curr_summary, new_summary))
        if args.log_json:
            _append_json_log(
                args.log_json,
                "preview",
                selected_target,
                new_target,
                links,
                backup_entry=(new_target, backup_path) if backup_path else None,
                link_mode=args.link_mode,
            )
        proceed = questionary.confirm("执行上述操作吗？", default=False).ask()
        if not proceed:
            print("已取消。")
            return 0
        # execute for real after confirmation
        try:
            migrate_target_and_update_links(
                selected_target,
                new_target,
                links,
                dry_run=False,
                conflict_strategy=conflict_strategy,
                backup_path=backup_path,
                data_root=data_root,
                link_mode=args.link_mode,
            )
        except MigrationError as e:
            print(f"执行失败：{e}")
            return 2
        if args.log_json:
            _append_json_log(
                args.log_json,
                "applied",
                selected_target,
                new_target,
                links,
                backup_entry=(new_target, backup_path) if backup_path else None,
                link_mode=args.link_mode,
            )
        # Final summary for new target after apply
        final_new = fast_tree_summary(new_target)
        print(f"summary(new=files:{final_new[0]} bytes:{final_new[1]})")
    else:
        # Non-dry-run invocation: operation already applied above
        final_new = fast_tree_summary(new_target)
        print(f"summary(new=files:{final_new[0]} bytes:{final_new[1]})")

    print("完成。已验证符号链接指向新目标。")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())



================================================
FILE: src/slm/config.py
================================================
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



================================================
FILE: src/slm/version.py
================================================
"""Version metadata for slm."""

__version__ = "0.1.0"


def get_version() -> str:
    return __version__


__all__ = ["__version__", "get_version"]



================================================
FILE: src/slm/core/__init__.py
================================================
"""Core primitives for scanning, migrating, and summarising symlink targets."""

from .migration import (
    MigrationError,
    _derive_backup_path,
    _safe_move_dir,
    migrate_target_and_update_links,
    rewrite_links_to_relative,
)
from .scanner import (
    SymlinkInfo,
    group_by_target_within_data,
    scan_symlinks_pointing_into_data,
)
from .summary import fast_tree_summary, format_summary_pair

__all__ = [
    "MigrationError",
    "SymlinkInfo",
    "_derive_backup_path",
    "_safe_move_dir",
    "fast_tree_summary",
    "format_summary_pair",
    "group_by_target_within_data",
    "migrate_target_and_update_links",
    "rewrite_links_to_relative",
    "scan_symlinks_pointing_into_data",
]



================================================
FILE: src/slm/core/migration.py
================================================
"""Directory migration primitives and safety helpers."""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Iterable, List, Optional

from .scanner import SymlinkInfo

class MigrationError(RuntimeError):
    pass


def _safe_move_dir(old: Path, new: Path) -> None:
    """Safe directory move; auto-creates parent directories; cross-device fallback."""

    if new.exists():
        raise MigrationError(f"Destination exists: {new}")

    try:
        new.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise MigrationError(f"Cannot create parent directory {new.parent}: {e}") from e

    try:
        old.rename(new)
    except OSError as e:
        if getattr(e, "errno", None) == 18 or "cross-device" in str(e).lower():
            shutil.copytree(old, new)
            shutil.rmtree(old)
        else:
            raise


def _derive_backup_path(target: Path, now: Optional[float] = None) -> Path:
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(now or time.time()))
    base = target.with_name(f"{target.name}~{timestamp}")
    candidate = base
    counter = 1
    while candidate.exists():
        candidate = target.with_name(f"{target.name}~{timestamp}-{counter}")
        counter += 1
    return candidate


def _retarget_symlink(link: Path, new_target: Path, *, make_relative: bool) -> None:
    if not link.is_symlink():
        raise MigrationError(f"Not a symlink: {link}")
    link.unlink()
    target_for_link = str(new_target)
    if make_relative:
        try:
            target_for_link = os.path.relpath(str(new_target), start=str(link.parent))
        except Exception:
            target_for_link = str(new_target)
    os.symlink(target_for_link, str(link))


def migrate_target_and_update_links(
    current_target: Path,
    new_target: Path,
    links: Iterable[Path],
    dry_run: bool = True,
    conflict_strategy: str = "abort",
    backup_path: Optional[Path] = None,
    data_root: Optional[Path] = None,
    link_mode: str = "relative",
) -> List[str]:
    actions: List[str] = []
    current_target = current_target.resolve()
    new_target = new_target.expanduser()
    links_list = list(links)

    valid_modes = {"relative", "absolute", "inline"}
    if link_mode not in valid_modes:
        raise MigrationError(f"Invalid link_mode: {link_mode}")
    use_relative_links = link_mode == "relative"
    materialize_links = link_mode == "inline"

    if not new_target.is_absolute():
        if data_root:
            new_target = (Path(data_root).resolve() / new_target).resolve()
        else:
            new_target = new_target.resolve()
    else:
        new_target = new_target.resolve()

    if current_target == new_target:
        raise MigrationError("New target equals current target.")
    try:
        current_target.relative_to("/")
        new_target.relative_to("/")
    except Exception:
        pass
    if str(new_target).startswith(str(current_target) + os.sep):
        raise MigrationError("New target cannot be inside current target.")

    backup_in_use: Optional[Path] = None
    if new_target.exists():
        if conflict_strategy == "abort":
            raise MigrationError(f"Destination exists: {new_target}")
        if conflict_strategy != "backup":
            raise MigrationError(f"Unsupported conflict strategy: {conflict_strategy}")
        backup_in_use = backup_path or _derive_backup_path(new_target)
        actions.append(f"Backup: {new_target} -> {backup_in_use}")

    actions.append(f"Move: {current_target} -> {new_target}")
    if materialize_links:
        for link in links_list:
            actions.append(f"Inline: {link} <= {new_target}")
    else:
        suffix = " (relative)" if use_relative_links else " (absolute)"
        for link in links_list:
            actions.append(f"Link: {link} -> {new_target}{suffix}")

    if dry_run:
        return actions

    if backup_in_use:
        if backup_in_use.exists():
            raise MigrationError(f"Backup destination exists: {backup_in_use}")
        try:
            new_target.rename(backup_in_use)
        except OSError as exc:
            raise MigrationError(f"Failed to backup existing destination: {exc}") from exc

    _safe_move_dir(current_target, new_target)
    if materialize_links:
        for link in links_list:
            if link.is_symlink():
                link.unlink()
            elif link.exists() and not link.is_dir():
                raise MigrationError(f"Cannot inline over existing non-dir: {link}")
            # When new_target shares the same path as one of the links, the move
            # above already materialised it; skip copying in that case.
            if link == new_target:
                continue
            shutil.copytree(new_target, link)
    else:
        for link in links_list:
            _retarget_symlink(link, new_target, make_relative=use_relative_links)

    if not new_target.exists():
        raise MigrationError(f"Move failed, missing: {new_target}")
    if materialize_links:
        for link in links_list:
            if not link.exists():
                raise MigrationError(f"Materialized path missing: {link}")
            if link.is_symlink():
                raise MigrationError(f"Materialized path still a symlink: {link}")
            if not link.is_dir():
                raise MigrationError(f"Materialized path is not a directory: {link}")
    else:
        for link in links_list:
            if Path(link).resolve(strict=True) != new_target:
                raise MigrationError(f"Verification failed for symlink: {link}")
    return actions


def rewrite_links_to_relative(
    infos: Iterable[SymlinkInfo], *, dry_run: bool = True
) -> List[str]:
    """Rewrite discovered symlinks to relative targets without moving data."""

    infos_list = list(infos)
    actions: List[str] = []

    def _compute_relative(link: Path, target: Path) -> str:
        try:
            return os.path.relpath(target, start=link.parent)
        except Exception as exc:
            raise MigrationError(f"无法计算相对路径: {link} -> {target}: {exc}") from exc

    for info in infos_list:
        rel = _compute_relative(info.source, info.target)
        actions.append(f"Retarget: {info.source} -> {rel} (target={info.target})")

    if dry_run:
        return actions

    for info in infos_list:
        _retarget_symlink(info.source, info.target, make_relative=True)

    for info in infos_list:
        if Path(info.source).resolve(strict=True) != info.target.resolve():
            raise MigrationError(f"Verification failed for symlink: {info.source}")
        raw = os.readlink(info.source)
        if os.path.isabs(raw):
            raise MigrationError(f"Link is still absolute: {info.source}")

    return actions


__all__ = [
    "MigrationError",
    "_safe_move_dir",
    "_derive_backup_path",
    "migrate_target_and_update_links",
    "rewrite_links_to_relative",
]



================================================
FILE: src/slm/core/scanner.py
================================================
"""Scanning helpers for discovering qualified symlink targets."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class SymlinkInfo:
    """Represents a directory symlink and its resolved absolute target."""

    source: Path
    target: Path


def _is_symlink_dir(p: Path) -> bool:
    try:
        return p.is_symlink() and p.resolve(strict=True).is_dir()
    except FileNotFoundError:
        return False


def _resolve_symlink_target_abs(p: Path) -> Path:
    """Resolve the symlink target, handling relative paths safely."""

    return p.resolve(strict=True)


def scan_symlinks_pointing_into_data(
    scan_roots: Iterable[Path],
    data_root: Path,
    excludes: Tuple[str, ...] = (
        ".git",
        "Library",
        ".cache",
        "node_modules",
        ".venv",
        "venv",
    ),
) -> List[SymlinkInfo]:
    data_root = data_root.resolve()
    found: List[SymlinkInfo] = []
    for root in scan_roots:
        root = root.expanduser().resolve()
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in excludes]
            for name in list(dirnames) + filenames:
                p = Path(dirpath) / name
                if not p.is_symlink():
                    continue
                try:
                    target = _resolve_symlink_target_abs(p)
                except FileNotFoundError:
                    continue
                if not target.is_dir():
                    continue
                try:
                    target.relative_to(data_root)
                except ValueError:
                    continue
                found.append(SymlinkInfo(source=p, target=target))
    return found


def group_by_target_within_data(
    infos: Iterable[SymlinkInfo], data_root: Path
) -> Dict[Path, List[SymlinkInfo]]:
    grouped: Dict[Path, List[SymlinkInfo]] = {}
    for info in infos:
        key = info.target
        grouped.setdefault(key, []).append(info)

    data_root = Path(data_root).resolve()

    def _sort_key(p: Path) -> str:
        try:
            rel = p.resolve().relative_to(data_root)
            return str(rel).lower()
        except Exception:
            return str(p.resolve()).lower()

    return dict(sorted(grouped.items(), key=lambda kv: _sort_key(kv[0])))


__all__ = [
    "SymlinkInfo",
    "scan_symlinks_pointing_into_data",
    "group_by_target_within_data",
]



================================================
FILE: src/slm/core/summary.py
================================================
"""Filesystem summary helpers used by the CLI."""

from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path
from typing import List, Tuple


def fast_tree_summary(path: Path) -> Tuple[int, int]:
    path = Path(path)
    if not path.exists() or not path.is_dir():
        return (0, 0)

    files = 0
    total_bytes = 0
    stack: List[Path] = [path]
    while stack:
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for entry in it:
                    with suppress(FileNotFoundError, PermissionError, OSError):
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                            continue
                        if entry.is_file(follow_symlinks=False):
                            files += 1
                            with suppress(FileNotFoundError, PermissionError, OSError):
                                st = entry.stat(follow_symlinks=False)
                                total_bytes += int(getattr(st, "st_size", 0))
        except (FileNotFoundError, PermissionError, NotADirectoryError, OSError):
            continue
    return (files, total_bytes)


def format_summary_pair(curr: Tuple[int, int], new: Tuple[int, int]) -> str:
    return (
        f"summary(current=files:{curr[0]} bytes:{curr[1]}, "
        f"new=files:{new[0]} bytes:{new[1]})"
    )


__all__ = ["fast_tree_summary", "format_summary_pair"]



================================================
FILE: src/slm/services/__init__.py
================================================
"""Service-layer helpers (configuration, IO integrations, etc.)."""

from .configuration import (
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



================================================
FILE: src/slm/services/configuration.py
================================================
"""Configuration loading utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:  # pragma: no cover - import tested indirectly
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
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
    except OSError as exc:  # pragma: no cover
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


def load_config(candidates: Optional[Iterable[Path]] = None) -> LoadedConfig:
    paths = list(candidates) if candidates is not None else list(DEFAULT_CONFIG_LOCATIONS)
    for raw in paths:
        candidate = raw.expanduser().resolve()
        if not candidate.exists():
            continue
        data = _load_yaml(candidate)
        return LoadedConfig(data=data, path=candidate)
    return LoadedConfig(data={}, path=None)


def coerce_scan_roots(value: Any, *, context: str) -> List[str]:
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


__all__ = [
    "ConfigError",
    "DEFAULT_CONFIG_LOCATIONS",
    "LoadedConfig",
    "coerce_scan_roots",
    "load_config",
]



================================================
FILE: tests/test_cli.py
================================================
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
    assert link_path.resolve() == new_target
    assert not os.path.isabs(os.readlink(link_path))
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
    assert not os.path.isabs(os.readlink(link_path))


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


def test_exit_choice_returns_string_without_crash(tmp_path, monkeypatch, capsys):
    """Ensure selecting the literal label '退出' exits cleanly (no KeyError)."""
    data_root = tmp_path / "Developer" / "Data"
    target = data_root / "project"
    target.mkdir(parents=True)

    # Create one symlink so the target selection menu is shown
    link_root = tmp_path / "links"
    link_root.mkdir()
    (link_root / "p").symlink_to(target)

    # Force the select prompt to return the label string instead of None
    from slm import cli

    monkeypatch.setattr(cli, "load_config", lambda: LoadedConfig(data={}, path=None))

    def fake_select(*args, **kwargs):
        return DummyPrompt("退出")

    monkeypatch.setattr(cli.questionary, "select", fake_select)

    exit_code = cli.main(["--data-root", str(data_root), "--scan-roots", str(link_root)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "已取消" in out


def test_inline_mode_materializes_links(tmp_path):
    """Inline mode removes symlinks and materializes directories in place."""
    data_root = tmp_path / "Data"
    current_target = data_root / "shared"
    current_target.mkdir(parents=True)
    (current_target / "file.txt").write_text("inline")

    link_a = tmp_path / "projectA" / "shared"
    link_a.parent.mkdir(parents=True)
    link_a.symlink_to(current_target)

    link_b = tmp_path / "projectB" / "shared"
    link_b.parent.mkdir(parents=True)
    link_b.symlink_to(current_target)

    new_target = data_root / "materialized"

    migrate_target_and_update_links(
        current_target,
        new_target,
        [link_a, link_b],
        dry_run=False,
        data_root=data_root,
        link_mode="inline",
    )

    assert not current_target.exists()
    assert new_target.exists()
    assert (new_target / "file.txt").read_text() == "inline"

    for path in (link_a, link_b):
        assert path.exists()
        assert not path.is_symlink()
        assert (path / "file.txt").read_text() == "inline"


def test_relative_only_mode_rewrites_symlinks(tmp_path, monkeypatch, capsys):
    """Relative-only mode rewrites existing links without moving targets."""
    data_root = tmp_path / "Data"
    target = data_root / "proj"
    target.mkdir(parents=True)
    (target / "f.txt").write_text("data")

    link_root = tmp_path / "links"
    link_root.mkdir()
    link_a = link_root / "a"
    link_a.symlink_to(target)
    link_b = link_root / "nested" / "b"
    link_b.parent.mkdir(parents=True)
    link_b.symlink_to(target)

    monkeypatch.setattr(cli, "load_config", lambda: LoadedConfig(data={}, path=None))

    def fake_confirm(*args, **kwargs):
        return DummyPrompt(True)

    monkeypatch.setattr(cli.questionary, "confirm", fake_confirm)

    exit_code = cli.main(
        ["--data-root", str(data_root), "--scan-roots", str(link_root), "--relative"]
    )
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "relative-only" in out
    assert target.exists()
    for link in (link_a, link_b):
        assert link.resolve() == target
        assert not os.path.isabs(os.readlink(link))
