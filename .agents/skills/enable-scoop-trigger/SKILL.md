---
name: enable-scoop-trigger
description: >
  Update an upstream repository to trigger the Scoop Bucket manifest update
  workflow upon release. Searches local workspace in /home/nicholas/git/nicholaswilde
  first before falling back to remote clone, verifies or sets the token secret
  (APT_REPO_TOKEN or SCOOP_REPO_TOKEN), updates .github/workflows/release.yml with the
  update-scoop-bucket dispatch job, and commits and pushes the changes.
  Trigger: /enable-scoop-trigger, /add-scoop-trigger, "update repo to trigger scoop",
  "enable scoop trigger", "add scoop trigger", "configure scoop trigger", "trigger scoop flow".
---

# Enable Scoop Trigger Skill

Protocol for configuring an upstream application repository to automatically
trigger the `update-manifest` workflow in `nicholaswilde/scoop-bucket`
whenever a new release tag is published.

## Inputs

- `<repo_name>` or `<owner>/<repo>`: Upstream application repository name
  (e.g. `tfa`, `enstow`, `proxmox-mcp-rs`).
- `[manifest_name]`: Manifest name in `bucket/<manifest>.json` (defaults to `<repo_name>`).
- `[secret_name]`: Secret name containing the GitHub PAT (defaults to
  `APT_REPO_TOKEN`, falling back to `SCOOP_REPO_TOKEN`).

## Tool Hygiene & Rules

- Pipe all GitHub CLI commands to `cat`: `rtk gh <command> | cat`.
- Prefix shell commands with `rtk` where subcommands exist (`rtk git`, `rtk gh`).
- Never echo or write plaintext token secrets to chat or committed files.

---

## Workflow Steps

### Step 1: Discover Repository (Local Workspace First)

Always check the local workspace directory `/home/nicholas/git/nicholaswilde`
first before using a remote clone:

```bash
REPO="<repo_name>" # e.g. "tfa"
LOCAL_DIR="/home/nicholas/git/nicholaswilde/${REPO}"

if [ -d "${LOCAL_DIR}" ]; then
  echo "Found local repository at: ${LOCAL_DIR}"
  cd "${LOCAL_DIR}"
else
  echo "Local repository not found in /home/nicholas/git/nicholaswilde/${REPO}."
  git clone "https://github.com/nicholaswilde/${REPO}.git" "/tmp/${REPO}"
  cd "/tmp/${REPO}"
fi
```

### Step 2: Verify Target Manifest in Bucket

Ensure the corresponding manifest exists in `bucket/<manifest_name>.json`:

```bash
BUCKET_DIR="/home/nicholas/git/nicholaswilde/scoop-bucket"
MANIFEST="${REPO}"

if [ ! -f "${BUCKET_DIR}/bucket/${MANIFEST}.json" ]; then
  echo "Warning: bucket/${MANIFEST}.json not found. Verify manifest name."
fi
```

### Step 3: Verify Token Secret on Target Repo

Verify that the target repository has `APT_REPO_TOKEN` (or `SCOOP_REPO_TOKEN`):

```bash
rtk gh secret list --repo "nicholaswilde/${REPO}" | cat
```

If missing, set it using `gh` (e.g. from `pass`):

```bash
rtk gh secret set APT_REPO_TOKEN --repo "nicholaswilde/${REPO}" \
  --body "$(pass github-apt-fine-grain-token)" | cat
```

### Step 4: Update Upstream Release Workflow (`.github/workflows/release.yml`)

In the target repository's `.github/workflows/release.yml`, inspect existing
jobs.

Add the `update-scoop-bucket` job to the end of the jobs list:

```yaml
  update-scoop-bucket:
    name: update-scoop-bucket
    needs: ['create-release', 'build-release']
    runs-on: ubuntu-latest
    if: github.ref_type == 'tag'
    steps:
      - name: Trigger Scoop Bucket update
        env:
          APT_REPO_TOKEN: ${{ secrets.APT_REPO_TOKEN }}
        run: |
          set -euo pipefail
          curl -f -X POST \
            -H "Authorization: token ${APT_REPO_TOKEN}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/nicholaswilde/scoop-bucket/dispatches \
            -d "{\"event_type\": \"update-manifest\", \"client_payload\": {\"manifest\": \"${MANIFEST}\", \"version\": \"${{ needs.create-release.outputs.version }}\"}}"
```

> [!IMPORTANT]
> Ensure `needs` includes both `create-release` and `build-release` so the
> dispatch fires only **after** Windows release archives (`.zip`) have finished
> uploading.

### Step 5: Verify, Commit, and Push Changes

Review the diff:

```bash
git diff .github/workflows/release.yml
```

Commit and push to remote `main`:

```bash
git add .github/workflows/release.yml
git commit -m "ci(release): dispatch update-manifest event to scoop-bucket"
git push origin main
```

### Step 6: Test Dispatch (Optional)

Trigger a manual test dispatch if desired:

```bash
rtk gh api repos/nicholaswilde/scoop-bucket/dispatches \
  --input - <<< '{"event_type": "update-manifest", "client_payload": {"manifest": "'"${MANIFEST}"'"}}' | cat
```
