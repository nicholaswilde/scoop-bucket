# Product Guidelines - scoop-bucket

## Scoop Manifest Standards
- **Schema Compliance**: Every manifest in `bucket/<appname>.json` must conform strictly to Scoop v1 manifest specifications.
- **Indentation & Formatting**: Maintain 4-space JSON indentation with a trailing newline.
- **Version Integrity**: Version field must match upstream release tag (stripped of `v` prefix).
- **Executable Mapping**: Explicitly list all binaries under `bin` (e.g. `["cook-docs.exe"]`).
- **URL Resolution**: Assets must point directly to stable GitHub release downloads with immutable tags.
- **Checksum Accuracy**: SHA256 hashes must always be computed from actual release downloads. Never fabricate hashes.

## Repository Hygiene
- **Secret Protection**: Never commit credentials, `.env` files, or private tokens.
- **Automated Validation**: Always validate manifests with `jq empty bucket/*.json` and `task audit`.
