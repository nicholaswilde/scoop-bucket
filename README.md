# 🍨 Scoop Bucket 🍨

The Scoop bucket for various Windows tools.

## 🚀 Usage

First, add the bucket:

```powershell
scoop bucket add nicholaswilde https://github.com/nicholaswilde/scoop-bucket.git
```

Then, install an application:

```powershell
scoop install nicholaswilde/<appname>
```

Or install directly if the bucket is known:

```powershell
scoop install <appname>
```

## 📦 Available Manifests

- `cook-docs`: A tool for automatically generating markdown documentation for cooklang recipes.
- `enstow`: 📦 Secret-aware dotfile manager combining stow symlinking with sops and age decryption in Rust 🦀
- `tfa`: 🔐 Fast, lightweight, and secure command-line Two-Factor Authentication (2FA/TOTP/HOTP) generator and manager in Rust 🦀

## 🛠️ Development

This project uses [Task](https://taskfile.dev/) for common development tasks.

### Auditing Manifests

Audit all manifests:
```bash
task audit
```

Audit a specific manifest:
```bash
task audit:cook-docs
```

### Testing Manifests

Test all manifests and python scripts:
```bash
task test
```

## 🤖 Automation

This repository is configured to automatically audit, test, and update manifests. It utilizes custom automation scripts and skills to streamline maintenance:
- `add-manifest`: Automates the creation of new manifests by fetching metadata and calculating SHA256 checksums from GitHub release assets.
- `update-manifest`: Autonomously scans upstream repositories for new releases and updates manifest versions and checksums.

## ⚖️ License

[Apache License 2.0](LICENSE)

## ✍️ Author

This project was started in 2022 by [Nicholas Wilde][1].

[1]: https://github.com/nicholaswilde/
