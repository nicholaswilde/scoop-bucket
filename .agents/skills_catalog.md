# Skills Catalog

| Skill | Description | Task / Command |
|---|---|---|
| [`add-manifest`](skills/add-manifest/SKILL.md) | Add a new Scoop manifest from upstream GitHub repository with asset hashing and integration. | `uv run scripts/add_manifest.py` or `/add-manifest` |
| [`enable-scoop-trigger`](skills/enable-scoop-trigger/SKILL.md) | Update an upstream repository to trigger the Scoop Bucket manifest update workflow upon release. | `/enable-scoop-trigger` / `/add-scoop-trigger` |
| [`update-manifest`](skills/update-manifest/SKILL.md) | Update an existing Scoop manifest in `bucket/` to latest release with checksum recalculation. | `uv run scripts/update_manifest.py` or `/update-manifest` |
