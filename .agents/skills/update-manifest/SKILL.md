---
name: update-manifest
description: >
  Update an existing Scoop manifest in this bucket to its latest upstream release.
  Scans upstream GitHub releases, compares versions, downloads assets, recalculates
  SHA256 checksums across Windows architectures (64bit, 32bit, arm64), updates
  bucket/<name>.json, and runs audit checks.
  Trigger: /update-manifest, "update manifest", "bump manifest", "upgrade manifest".
---

# Update Manifest Skill

Automate updating an existing Scoop manifest in `bucket/` to its latest upstream release version, updating URLs, recalculating SHA256 checksums across architectures, and verifying with `jq`.

## Invocation

```text
/update-manifest [manifest_name] [dry_run]
```
- `[manifest_name]`: Name of manifest in `bucket/` (fuzzy match supported by helper script).
- `[dry_run]`: Pass `--dry-run` to preview changes without modifying files.

## Protocol

### Step 1: Manifest Discovery
1. Identify target manifest file `bucket/<manifest_name>.json`.
2. If `manifest_name` is omitted or partial, use `scripts/find_manifest.py` to identify the best match:
   ```bash
   uv run python scripts/find_manifest.py <query>
   ```
3. Read the manifest to determine the current `version` and upstream GitHub repository from `homepage` or `url`.

### Step 2: Upstream Release Check
1. Fetch latest stable release from the upstream repository.
   - When using `gh`, always pipe to `cat` to prevent interactive pager hang:
     ```bash
     gh release view --repo <owner>/<repo> --json tagName,assets | cat
     ```
2. Compare upstream release tag (stripping leading `v`) against current `version` in manifest.
3. If already at latest version, report that manifest is up to date and exit early.

### Step 3: Asset Recalculation & Manifest Update
1. Automated update via script:
   - For preview / dry-run:
     ```bash
     uv run scripts/update_manifest.py <manifest_name> --dry-run
     ```
   - For applying update:
     ```bash
     uv run scripts/update_manifest.py <manifest_name>
     ```
   - For specific version override:
     ```bash
     uv run scripts/update_manifest.py <manifest_name> --version-override <version>
     ```
2. **Architecture Mapping**:
   - Verify assets for `64bit`, `32bit`, and `arm64`.
   - Update download URLs and recalculate SHA256 hashes (`hash`).
3. Maintain 4-space indentation and JSON syntax integrity.
4. Never commit `.env` or files containing secret tokens or credentials.

### Step 4: Verification
1. Run JSON syntax audit check:
   ```bash
   task audit:<manifest_name>
   ```
2. Run script tests:
   ```bash
   uv run python -m unittest discover -s scripts
   ```
3. Summarize version bump (old version -> new version) and updated architectures.
