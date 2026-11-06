import argparse
import hashlib
import json
import os
import re
import sys
from urllib.request import urlopen

from github_utils import create_github_request, get_github_token


def get_repo_details(repo, token=None):
    url = f"https://api.github.com/repos/{repo}"
    req = create_github_request(url, token=token)

    with urlopen(req) as response:
        data = json.loads(response.read().decode())
        return {
            "description": data.get("description", ""),
            "homepage": data.get("homepage") or data.get("html_url", ""),
            "license": data.get("license", {}).get("spdx_id", "Apache-2.0")
            if data.get("license")
            else "Apache-2.0",
        }


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


def map_windows_assets(assets):
    mapping = {
        "64bit": [
            r"Windows_x86_64",
            r"x86_64-pc-windows",
            r"win64",
            r"windows-amd64",
            r"Windows_amd64",
        ],
        "32bit": [
            r"Windows_i386",
            r"i686-pc-windows",
            r"win32",
            r"windows-386",
            r"Windows_x86_32",
        ],
        "arm64": [
            r"Windows_arm64",
            r"aarch64-pc-windows",
            r"win-arm64",
            r"windows-arm64",
        ],
    }

    result = {}
    for arch, patterns in mapping.items():
        for asset in assets:
            name = asset["name"]
            if any(re.search(p, name, re.IGNORECASE) for p in patterns) and (
                name.endswith(".zip")
                or name.endswith(".tar.gz")
                or name.endswith(".exe")
            ):
                result[arch] = {
                    "url": asset["browser_download_url"],
                    "filename": name,
                }
                break
    return result


def generate_manifest(app_name, details, version, mapped_assets, bin_name=None):
    binary = bin_name or f"{app_name}.exe"
    architecture = {}

    for arch, info in mapped_assets.items():
        architecture[arch] = {
            "url": info["url"],
            "bin": [binary],
            "hash": info.get("sha256", ""),
        }

    manifest = {
        "version": version,
        "architecture": architecture,
        "homepage": details.get("homepage", ""),
        "license": details.get("license", "Apache-2.0"),
        "description": details.get("description", ""),
    }
    return manifest


def update_taskfile(manifest_name, taskfile_path="Taskfile.yml"):
    if not os.path.isfile(taskfile_path):
        return

    with open(taskfile_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    in_audit_task = False
    in_audit_cmds = False
    added_to_unified = False

    for i, line in enumerate(lines):
        new_lines.append(line)
        if line.strip() == "audit:":
            in_audit_task = True
        elif in_audit_task and line.strip() == "cmds:":
            in_audit_cmds = True
        elif (
            in_audit_cmds
            and line.strip().startswith("- task: audit:")
            and not added_to_unified
        ):
            if f"- task: audit:{manifest_name}" in line:
                added_to_unified = True
            elif (
                i + 1 >= len(lines)
                or not lines[i + 1].strip().startswith("- task: audit:")
            ):
                new_lines.append(f"      - task: audit:{manifest_name}\n")
                added_to_unified = True

    if not any(f"audit:{manifest_name}:" in line for line in lines):
        new_lines.append(f"\n  audit:{manifest_name}:\n")
        new_lines.append(f"    desc: Audit {manifest_name} manifest\n")
        new_lines.append("    cmds:\n")
        new_lines.append(f"      - jq empty bucket/{manifest_name}.json\n")

    with open(taskfile_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def update_readme(manifest_name, description, readme_path="README.md"):
    if not os.path.isfile(readme_path):
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    entry = f"- `{manifest_name}`: {description}"
    if entry in content or f"`{manifest_name}`" in content:
        return

    # Look for Available Manifests list
    pattern = r"(## 📦 Available Manifests\n\n)([\s\S]*?)(\n\n## )"
    match = re.search(pattern, content)
    if match:
        existing_list = match.group(2).strip().split("\n")
        existing_list.append(entry)
        existing_list.sort()
        new_section = match.group(1) + "\n".join(existing_list) + match.group(3)
        content = content[: match.start()] + new_section + content[match.end() :]
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(description="Add a new Scoop manifest")
    parser.add_argument("manifest_name", help="Name of the manifest to create")
    parser.add_argument(
        "owner",
        nargs="?",
        default="nicholaswilde",
        help="GitHub owner (default: nicholaswilde)",
    )
    parser.add_argument(
        "--repo", help="GitHub repository name (defaults to manifest_name)"
    )
    parser.add_argument("--bin", help="Executable binary name (e.g. app.exe)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--env-file", default=".env", help="Path to .env file (default: .env)"
    )
    args = parser.parse_args()

    token = get_github_token(args.env_file)
    repo_name = args.repo if args.repo else args.manifest_name
    repo = f"{args.owner}/{repo_name}"
    print(f"Adding manifest {args.manifest_name} for repository: {repo}")

    try:
        details = get_repo_details(repo, token=token)
        print(f"Fetched details: {details}")

        version, assets = get_latest_release(repo, token=token)
        print(f"Latest version: {version}")

        mapped_assets = map_windows_assets(assets)
        if not mapped_assets:
            print(
                f"Warning: No Windows assets found in release {version} for {repo}"
            )
            mapped_assets["64bit"] = {
                "url": f"https://github.com/{repo}/releases/download/v{version}/{repo_name}_{version}_Windows_x86_64.tar.gz",
                "filename": f"{repo_name}_{version}_Windows_x86_64.tar.gz",
            }

        print(f"Mapped assets: {list(mapped_assets.keys())}")

        for arch, info in mapped_assets.items():
            try:
                print(f"Calculating checksum for {arch} ({info['url']})...")
                info["sha256"] = calculate_sha256(info["url"])
                print(f"Checksum: {info['sha256']}")
            except Exception as e:
                print(f"Could not download asset to compute hash: {e}")
                info["sha256"] = ""

        manifest_data = generate_manifest(
            args.manifest_name,
            details,
            version,
            mapped_assets,
            bin_name=args.bin,
        )
        manifest_path = f"bucket/{args.manifest_name}.json"
        manifest_json = json.dumps(manifest_data, indent=4, ensure_ascii=False) + "\n"

        if args.dry_run:
            print(f"--- DRY RUN: Proposed Manifest {manifest_path} ---")
            print(manifest_json)
            print("--- DRY RUN: Taskfile and README updates previewed ---")
        else:
            os.makedirs("bucket", exist_ok=True)
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(manifest_json)
            print(f"Successfully created {manifest_path}")

            update_taskfile(args.manifest_name)
            print("Successfully updated Taskfile.yml")

            update_readme(
                args.manifest_name,
                details.get("description", "A tool for Windows"),
            )
            print("Successfully updated README.md")

    except Exception as e:
        print(f"Error creating manifest: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
