# Agent CLI - Scoop Bucket Context

This file provides instructions and context for AI agents working on this repository.

## Project Structure
- `bucket/`: Contains Scoop manifest JSON files (`<appname>.json`).
- `scripts/`: Contains Python automation scripts (`add_manifest.py`, `update_manifest.py`, `find_manifest.py`, `github_utils.py`) and unit tests.
- `.agents/conductor/`: Contains project management, definition, tech stack, and workflow documents.
- `.agents/rules/`: Symlinks to standard agentic rules.
- `.agents/skills/`: Custom project skills (`add-manifest`, `update-manifest`).
- `.agents/skills_catalog.md`: Catalog of available project skills.

## Guidelines for Manifest Updates
When updating or adding Scoop manifests:
1. **Maintain Style**: Adhere to Scoop JSON manifest conventions (4-space indentation, standard key ordering).
2. **Version Consistency**: Ensure `version` matches the release tag (without 'v' prefix).
3. **Architecture Mapping**: Verify URLs and executables under `architecture` (e.g. `64bit`, `32bit`, `arm64`) point to the correct Windows release assets.
4. **Checksums**: Always compute exact SHA256 checksums from release assets. Never guess or fabricate hashes.
5. **Validation**: Validate JSON syntax using `jq empty bucket/<app>.json` or `task audit:<app>` before completing tasks.

## Automated Update Workflow
You are an automated Scoop manifest updater. Your goal is to keep manifests in the 'bucket/' directory up-to-date with their upstream GitHub releases.

1. **Scan and Parse**: Identify the target manifest(s). Read the `.json` file(s) and identify the upstream GitHub repository from `homepage` or `url`.
2. **Check for Updates**: For each manifest, use the GitHub CLI (`rtk gh release view --json tagName,assets | cat`) or GitHub API to find the latest stable release.
3. **Compare Versions**: Compare latest `tagName` (removing any 'v' prefix) with the `version` field in the manifest. Proceed only if a newer version is available.
4. **Update Assets**:
   a. Identify required Windows assets (`64bit`, `32bit`, `arm64`).
   b. Download assets and calculate SHA256 checksums.
   c. Update the `version` string.
   d. Update the `url` and `hash` strings within `architecture`.
   e. Ensure `bin` lists correct executable name(s) (e.g. `["app.exe"]`).
5. **Maintain Integrity**: Ensure JSON remains valid with 4-space indentation and trailing newline.
6. **Verify**: Run `task audit` and `task test` to ensure all manifests and scripts pass validation.

## Tool Usage
You have access to the shell. Use standard tools like `curl`, `sha256sum`, `gh` (GitHub CLI), `jq`, and `uv` to perform your tasks.
1. When running `gh` commands, always use `rtk` and pipe to `cat` (e.g., `rtk gh release view --json tagName,assets | cat`) to filter output and prevent hanging in interactive pagers.
2. For executing Python scripts in this repository, always use `uv run` (e.g., `uv run scripts/update_manifest.py <manifest_name>`) to ensure consistent environment and dependency resolution.

<!-- rtk-begin -->
## RTK (`rtk`) Command Proxy

Prefix raw shell commands with `rtk` whenever subcommand exists. `rtk` filters and compresses output before model context.

### Command Map

| Raw | Use |
|---|---|
| `git <cmd>` | `rtk git <cmd>` |
| `gh <cmd>` | `rtk gh <cmd> \| cat` |
| `rg` / `grep` | `rtk rg` / `rtk grep` |
| `ls` / `tree` / `find` | `rtk ls` / `rtk tree` / `rtk find` |
| `cat <file>` (to inspect) | `rtk read <file>` |
| `diff` | `rtk diff` |
| `wc` | `rtk wc` |
| tests / checks (`task audit`, `task test`) | `rtk test <cmd>` or `rtk err <cmd>` |
| build / lint | `rtk err <cmd>` |
| noisy output | `rtk summary <cmd>` |

### Exceptions

1. **ctx sandbox**: inside `ctx_execute` / `ctx_batch_execute`, skip `rtk`; only printed output enters context.
2. **Exact output needed**: drop `rtk` when raw bytes matter (`git diff` patch, verbatim file edit).
3. **No subcommand**: run commands without `rtk` subcommand raw (`mkdir`, `rm`, `jq`, `uv run`).
4. **Unknown**: check `rtk --help` before assuming subcommand exists.
<!-- rtk-end -->

<!-- context-mode-begin -->
## Context-Mode Routing Guidelines
- **Derive, Do Not Dump**: Do NOT use `ctx_execute_file` or `ctx_execute` to dump whole file or full config. Print only specific value, matches, count, or known line range needed.
- **Tool Call Surface**: When using MCP wrappers, call `call_mcp_tool` with `ServerName: "context-mode_context-mode"` (or `"context-mode"`) and `ToolName: "ctx_execute"`, `"ctx_execute_file"`, `"ctx_batch_execute"`, `"ctx_fetch_and_index"`, `"ctx_search"`, or `"ctx_index"`.
- **Mandatory Routing**:
  - For analyze/count/filter/compare/search/parse/transform tasks, write code with `ctx_execute` and print only final answer.
  - For analyzing/exploring inside file, use `ctx_execute_file`. Use native `read_file` only when editing requires exact bytes or small known range.
  - Use `ctx_batch_execute` for multi-command repository reconnaissance.
  - Use `ctx_execute` for shell commands whose output may exceed short fixed answer.
  - Use `ctx_fetch_and_index` for web content, then `ctx_search` to query it.
  - Return only derived answers, concise summaries, selected snippets, or file paths.
<!-- context-mode-end -->

<!-- ponytail-begin -->
## Ponytail (Lazy Senior Dev Mode) Guidelines
- **Stop at the first rung that holds**:
  1. Does this need to be built at all? (YAGNI)
  2. Does it already exist in this codebase? Reuse existing helpers/utils/patterns.
  3. Does the standard library already do this?
  4. Does a native platform feature cover it?
  5. Does an already-installed dependency solve it?
  6. Can this be one line?
  7. Only then: write the minimum code that works.
- **Bug fix = root cause, not symptom**: Fix the shared function/path rather than individual callers.
- **Rules**:
  - No unrequested abstractions, boilerplate, or avoidable dependencies.
  - Deletion over addition. Boring over clever. Fewest files possible.
  - Shortest working diff wins, once the problem is understood.
  - Mark deliberate simplifications cutting a real corner with a `ponytail:` comment naming the ceiling and upgrade path.
  - Ensure logic leaves behind ONE runnable check (assert-based demo/self-check or small test file; no frameworks/fixtures). Trivial one-liners need no test.
<!-- ponytail-end -->

<!-- caveman-begin -->
## Caveman Guidelines
Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:
- Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging.
- Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- Pattern: [thing] [action] [reason]. [next step].
- Not: "Sure! I'd be happy to help you with that."
- Yes: "Bug in auth middleware. Fix:"

Switch level: /caveman lite|full|ultra|wenyan
Stop: "stop caveman" or "normal mode"

Auto-Clarity: drop caveman for security warnings, irreversible actions, user confused. Resume after.

Boundaries: code/commits/PRs written normal.
<!-- caveman-end -->

<!-- codegraph-begin -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- codegraph-end -->

<!-- serena-begin -->
## Serena Semantic Code Tools

Serena MCP provides Language Server Protocol (LSP) backed semantic coding tools, token-efficient AST symbol search, reference-aware refactoring, and persistent project memories.

- **Project Activation**: When Serena is available, ensure the workspace is active before querying code.
- **Symbol Inspection Over File Dumps**: Do not dump entire source code files into context. Use `get_symbols_overview` for a high-level view of symbols in a file, or `find_symbol` to retrieve specific classes, functions, or methods with their bodies.
- **Pattern & Reference Search**: Use `search_for_pattern` to locate symbols when the exact path is unknown, and `find_referencing_symbols` to analyze blast radius and callers.
- **Atomic Refactoring**: Prefer Serena's reference-aware editing tools (`rename_symbol`, `safe_delete_symbol`, `replace_symbol_body`) over manual regex or line-based text edits when refactoring existing symbols.
- **Persistent Memory**: Use `read_memory`, `write_memory`, and `list_memories` to retrieve or store durable project facts and conventions across agent sessions.
- **Diagnostics**: Use `get_diagnostics_for_file` to inspect LSP compiler/linter warnings and errors on modified files.
<!-- serena-end -->

<!-- headroom-begin -->
## Headroom MCP (Context Window Compression)
Use Headroom (`headroom`) MCP tools to manage context window consumption on large payloads:
- `headroom_compress`: Shrink large tool outputs or raw data.
- `headroom_retrieve`: Retrieve original content by hash if specific details needed.
- `headroom_stats`: Monitor headroom cache usage.
<!-- headroom-end -->

<!-- ripgrep-guidelines-begin -->
## Ripgrep Guidelines
- **Pattern Searching**: Always use `rg` (ripgrep) or `rtk rg` instead of standard `grep` to search text inside files quickly and save token output.
- **Scope**: Keep context small (`-C 1`), use `-l` for file listing.
<!-- ripgrep-guidelines-end -->

<!-- taplo-rules-begin -->
## Taplo TOML Rules
- **Format**: Run `rtk taplo fmt` to format TOML files in-place (`pyproject.toml`).
- **Validation**: Run `rtk taplo lint` to validate TOML syntax and schema.
<!-- taplo-rules-end -->

<!-- sensitive-information-protection-begin -->
## Sensitive Information & Secret Protection
NEVER commit or stage sensitive personal, financial, or security data to repository:
1. **Secrets & Credentials**: Never commit `.env` files, API keys, bearer tokens, passwords, or private encryption keys.
2. **Explicit Staging**: Never use `git add .` when untracked secret files exist; stage explicitly by name.
<!-- sensitive-information-protection-end -->

<!-- issue-management-begin -->
## GitHub Issue Management
- GitHub issues only close automatically when commits containing `Fixes #<number>` are pushed to remote repository.
<!-- issue-management-end -->
