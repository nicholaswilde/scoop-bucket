# Tech Stack - scoop-bucket

## Core Platform
- **Scoop:** The primary command-line installer and package manager for Windows.
- **Manifest Format:** JSON (Scoop application manifest schema v1).

## Development & Automation
- **Python:** Language used for manifest discovery, asset calculation, and update automation scripts (`scripts/`).
- **uv:** Ultra-fast Python package and environment manager.
- **GoReleaser:** Used as upstream release automation tool to generate manifest updates and manage release artifacts.
- **Taskfile:** Orchestrates local validation, auditing, and test suites.
- **GitHub Actions:** CI/CD platform for validating manifests and automated repository maintenance.
- **Gemini CLI:** AI agent workflows and custom commands (`add-manifest`, `update-manifest`).

## Target Architectures
- **Windows:**
  - `64bit`: `x86_64` / AMD64
  - `32bit`: `i386` / x86
  - `arm64`: AArch64 / ARM64
