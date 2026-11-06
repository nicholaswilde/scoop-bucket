import os
from urllib.request import Request


def load_env_file(filepath=".env"):
    """Parse a simple KEY=VALUE .env file if it exists."""
    env_vars = {}
    candidates = [filepath]
    if filepath == ".env":
        repo_root_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if repo_root_env not in candidates:
            candidates.append(repo_root_env)

    for path in candidates:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in env_vars:
                        env_vars[key] = val
            break
    return env_vars


def get_github_token(env_file=".env"):
    """Get GitHub token from .env file (primary) or environment variables (secondary).

    Returns None if no token is found.
    """
    file_vars = load_env_file(env_file)
    token = file_vars.get("GITHUB_TOKEN") or file_vars.get("GH_TOKEN")
    if token:
        return token
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def create_github_request(url, token=None):
    """Create a Request with User-Agent and optional Authorization header."""
    req = Request(url)
    req.add_header("User-Agent", "Gemini-CLI-Scoop-Updater")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    return req
