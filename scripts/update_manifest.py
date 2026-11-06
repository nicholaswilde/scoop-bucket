import argparse
import hashlib
import json
import os
import re
import sys
from urllib.request import urlopen

from find_manifest import find_manifest
from github_utils import create_github_request, get_github_token


def extract_github_repo(manifest_data):
    """Extract owner/repo from URLs found in architecture."""
    arch_data = manifest_data.get("architecture", {})
    for arch, arch_info in arch_data.items():
        url = arch_info.get("url", "")
        match = re.search(r"https://github\.com/([^/]+)/([^/]+)/", url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"

    # Check top-level url if architecture is absent
    url = manifest_data.get("url", "")
    match = re.search(r"https://github\.com/([^/]+)/([^/]+)/", url)
    if match:
        return f"{match.group(1)}/{match.group(2)}"

    # Check homepage
    homepage = manifest_data.get("homepage", "")
    match = re.search(r"https://github\.com/([^/]+)/([^/]+)", homepage)
    if match:
        return f"{match.group(1)}/{match.group(2)}"

    return None


def get_latest_release(repo, token=None):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = create_github_request(url, token=token)

    with urlopen(req) as response:
        data = json.loads(response.read().decode())
        return data["tag_name"].lstrip("v"), data["assets"]


def calculate_sha256(url, timeout=30):
    sha256_hash = hashlib.sha256()
    with urlopen(url, timeout=timeout) as response:
        for byte_block in iter(lambda: response.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def update_manifest_data(manifest_data, new_version, assets):
    old_version = manifest_data.get("version", "unknown")
    manifest_data["version"] = new_version

    arch_data = manifest_data.get("architecture", {})
    for arch, arch_info in arch_data.items():
        old_url = arch_info.get("url", "")
        # Update version in URL
        new_url = re.sub(
            r"/download/v?[^/]+/", f"/download/v{new_version}/", old_url
        )
        new_url = re.sub(
            r"([-_])[0-9]+\.[0-9]+\.[0-9]+", r"\g<1>" + new_version, new_url
        )
        arch_info["url"] = new_url

        # Match filename in release assets
        filename_match = re.search(r"/([^/]+)$", new_url)
        if filename_match:
            target_filename = filename_match.group(1)
            asset = next(
                (a for a in assets if a["name"] == target_filename), None
            )
            if asset:
                download_url = asset["browser_download_url"]
                arch_info["url"] = download_url
                print(f"Calculating hash for {target_filename}...")
                arch_info["hash"] = calculate_sha256(download_url)
            else:
                try:
                    print(
                        f"Attempting download to calculate hash for {new_url}..."
                    )
                    arch_info["hash"] = calculate_sha256(new_url)
                except Exception as e:
                    print(f"Warning: Could not fetch hash for {new_url}: {e}")

    return manifest_data, old_version


def main():
    parser = argparse.ArgumentParser(description="Update Scoop manifest")
    parser.add_argument(
        "manifest_name", nargs="?", help="Name of the manifest to update"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--version-override", help="Force update to a specific version"
    )
    parser.add_argument(
        "--env-file", default=".env", help="Path to .env file (default: .env)"
    )
    args = parser.parse_args()

    token = get_github_token(args.env_file)
    match, all_manifests = find_manifest(args.manifest_name)

    if not match:
        if args.manifest_name:
            print(f"Error: Could not find manifest matching '{args.manifest_name}'")
        else:
            print("Error: No manifest name provided.")
        print("Available manifests:", ", ".join(all_manifests))
        sys.exit(1)

    print(f"Selected manifest: {match}")
    manifest_path = f"bucket/{match}.json"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    repo = extract_github_repo(manifest_data)
    if not repo:
        print(f"Error: Could not find GitHub repository in {manifest_path}")
        sys.exit(1)

    print(f"Upstream repository: {repo}")

    if args.version_override:
        latest_version = args.version_override
        print(f"Using version override: {latest_version}")
        assets = []
    else:
        try:
            latest_version, assets = get_latest_release(repo, token=token)
            print(f"Latest version: {latest_version}")
        except Exception as e:
            print(f"Error fetching latest release from GitHub: {e}")
            sys.exit(1)

    old_version = manifest_data.get("version", "unknown")
    if old_version == latest_version and not args.version_override:
        print(f"Manifest {match} is already up to date ({latest_version}).")
        return

    updated_data, old_ver = update_manifest_data(
        manifest_data, latest_version, assets
    )
    new_json = json.dumps(updated_data, indent=4) + "\n"

    if args.dry_run:
        print(
            f"--- DRY RUN: Proposed Changes for {match} ({old_ver} -> {latest_version}) ---"
        )
        print(new_json)
    else:
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(new_json)
        print(
            f"Successfully updated {manifest_path} ({old_ver} -> {latest_version})"
        )


if __name__ == "__main__":
    main()
