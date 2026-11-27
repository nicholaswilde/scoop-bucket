import os
import tempfile
import unittest
from unittest.mock import patch

from add_manifest import generate_manifest, map_windows_assets
from find_manifest import find_manifest
from update_manifest import update_manifest_data


class TestManifestLogic(unittest.TestCase):

    def test_map_windows_assets(self):
        assets = [
            {
                "name": "cook-docs_0.6.1_Linux_x86_64.tar.gz",
                "browser_download_url": "https://example.com/linux.tar.gz",
            },
            {
                "name": "cook-docs_0.6.1_Windows_x86_64.tar.gz",
                "browser_download_url": "https://example.com/windows_x86_64.tar.gz",
            },
            {
                "name": "cook-docs_0.6.1_Windows_arm64.zip",
                "browser_download_url": "https://example.com/windows_arm64.zip",
            },
        ]
        mapped = map_windows_assets(assets)
        self.assertIn("64bit", mapped)
        self.assertIn("arm64", mapped)
        self.assertNotIn("32bit", mapped)
        self.assertEqual(
            mapped["64bit"]["url"], "https://example.com/windows_x86_64.tar.gz"
        )
        self.assertEqual(
            mapped["arm64"]["url"], "https://example.com/windows_arm64.zip"
        )

    def test_generate_manifest(self):
        details = {
            "description": "Test description",
            "homepage": "https://example.com",
            "license": "Apache-2.0",
        }
        mapped_assets = {
            "64bit": {
                "url": "https://example.com/tool_1.0.0_Windows_x86_64.zip",
                "sha256": "abcdef123456",
            }
        }
        manifest = generate_manifest("tool", details, "1.0.0", mapped_assets)
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual(
            manifest["architecture"]["64bit"]["url"],
            "https://example.com/tool_1.0.0_Windows_x86_64.zip",
        )
        self.assertEqual(
            manifest["architecture"]["64bit"]["hash"], "abcdef123456"
        )
        self.assertEqual(manifest["architecture"]["64bit"]["bin"], ["tool.exe"])

    @patch("update_manifest.calculate_sha256", return_value="mocked_hash_value")
    def test_update_manifest_data(self, mock_hash):
        manifest_data = {
            "version": "0.1.0",
            "architecture": {
                "64bit": {
                    "url": "https://github.com/org/repo/releases/download/v0.1.0/repo_0.1.0_Windows_x86_64.zip",
                    "bin": ["repo.exe"],
                    "hash": "old_hash",
                }
            },
        }
        assets = [
            {
                "name": "repo_0.2.0_Windows_x86_64.zip",
                "browser_download_url": "https://github.com/org/repo/releases/download/v0.2.0/repo_0.2.0_Windows_x86_64.zip",
            }
        ]
        updated, old_ver = update_manifest_data(manifest_data, "0.2.0", assets)
        self.assertEqual(old_ver, "0.1.0")
        self.assertEqual(updated["version"], "0.2.0")
        self.assertIn("v0.2.0", updated["architecture"]["64bit"]["url"])
        self.assertEqual(
            updated["architecture"]["64bit"]["hash"], "mocked_hash_value"
        )
        self.assertNotIn("extract_dir", updated["architecture"]["64bit"])

    @patch("update_manifest.calculate_sha256", return_value="mocked_hash_value")
    def test_update_manifest_data_updates_extract_dir(self, mock_hash):
        manifest_data = {
            "version": "0.9.6",
            "architecture": {
                "64bit": {
                    "url": "https://github.com/org/repo/releases/download/v0.9.6/repo_0.9.6_Windows_x86_64.zip",
                    "extract_dir": "repo_0.9.6_Windows_x86_64",
                    "bin": ["repo.exe"],
                    "hash": "old_hash",
                }
            },
        }
        assets = [
            {
                "name": "repo_0.9.7_Windows_x86_64.zip",
                "browser_download_url": "https://github.com/org/repo/releases/download/v0.9.7/repo_0.9.7_Windows_x86_64.zip",
            }
        ]
        updated, _ = update_manifest_data(manifest_data, "0.9.7", assets)
        self.assertEqual(
            updated["architecture"]["64bit"]["extract_dir"],
            "repo_0.9.7_Windows_x86_64",
        )

    def test_find_manifest_exact_vs_fuzzy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "hbx.json"), "w", encoding="utf-8").close()

            match_exact, manifests = find_manifest(
                "hbctl", bucket_dir=tmpdir, exact=True
            )
            self.assertIsNone(match_exact)
            self.assertEqual(manifests, ["hbx"])

            match_fuzzy, _ = find_manifest(
                "hbctl", bucket_dir=tmpdir, exact=False
            )
            self.assertEqual(match_fuzzy, "hbx")

            open(os.path.join(tmpdir, "hbctl.json"), "w", encoding="utf-8").close()
            match_found, _ = find_manifest(
                "hbctl", bucket_dir=tmpdir, exact=True
            )
            self.assertEqual(match_found, "hbctl")


if __name__ == "__main__":
    unittest.main()
