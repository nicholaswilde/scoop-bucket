---
name: add-manifest
description: >
  Add a new Scoop manifest to this bucket from an upstream GitHub repository.
  Fetches repository metadata and latest release assets, calculates SHA256 checksums
  for Windows architectures (64bit, 32bit, arm64), generates bucket/<name>.json,
  adds audit tasks to Taskfile.yml, and updates README.md.
  Trigger: /add-manifest, "add manifest", "create manifest", "new manifest", "add scoop manifest".
---

# Add Manifest Skill

Automate adding a new Scoop manifest to this bucket by querying the upstream GitHub repository, downloading Windows release assets, computing SHA256 checksums, generating the JSON manifest file, and integrating with `Taskfile.yml` and `README.md`.

## Invocation

```text
/add-manifest <repo_name> [owner] [--dry-run]
```
- `<repo_name>`: Upstream GitHub repository name (or manifest name).
- `[owner]`: GitHub organization or username (defaults to `nicholaswilde`).
- `[--dry-run]`: Preview generated manifest and modifications without writing changes.

## Protocol

### Step 1: Upstream Discovery & Metadata
1. Resolve repository coordinates:
   - Default owner: `nicholaswilde` unless explicitly provided.
   - Target repo: `<owner>/<repo_name>`.
2. Discover repository details and latest release:
   - Query repository metadata (description, homepage, license) and latest release assets.
   - When using `gh`, always pipe to `cat` to prevent interactive pager hang:
     ```bash
     gh release view --repo <owner>/<repo_name> --json tagName,assets | cat
     ```
   - Alternatively, preview via `uv run scripts/add_manifest.py <repo_name> [owner] --dry-run`.
   - Never commit `.env` or files containing secret tokens or credentials.

### Step 2: Windows Asset Mapping & Checksums
1. Locate release assets for Windows architectures:
   - **64bit**: `*Windows_x86_64*`, `*x86_64-pc-windows*`, `*win64*.zip`, `*.tar.gz`
   - **32bit**: `*Windows_i386*`, `*i686-pc-windows*`, `*win32*.zip`
   - **arm64**: `*Windows_arm64*`, `*aarch64-pc-windows*.zip`
2. Download artifacts and compute exact SHA256 checksums (`calculate_sha256`). Do not guess or reuse old hashes.

### Step 3: Manifest Generation
1. Target file: `bucket/<manifest_name>.json`.
2. Script execution:
   ```bash
   uv run scripts/add_manifest.py <manifest_name> [owner]
   ```
3. Ensure formatting adheres to 4-space indentation Scoop standards.

### Step 4: Taskfile.yml Integration
1. Add an individual audit task to `Taskfile.yml`:
   ```yaml
     audit:<manifest_name>:
       desc: Audit <manifest_name> manifest
       cmds:
         - jq empty bucket/<manifest_name>.json
   ```
2. Append `- task: audit:<manifest_name>` to the unified `audit` task in `Taskfile.yml`.
   *(Note: `scripts/add_manifest.py` automates this step if executed directly).*

### Step 5: README.md Integration
1. Add the new manifest to the `📦 Available Manifests` list in `README.md` in alphabetical order.
2. Include short description:
   ```markdown
   - `<manifest_name>`: <description>
   ```

### Step 6: Verification
1. Validate JSON syntax:
   ```bash
   jq empty bucket/<manifest_name>.json
   ```
2. Run audit task:
   ```bash
   task audit:<manifest_name>
   ```
3. Run python test suite:
   ```bash
   uv run python -m unittest discover -s scripts
   ```
4. Output concise summary with manifest path, version, and architecture coverage.
