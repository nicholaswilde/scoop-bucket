import unittest
from unittest.mock import patch

from add_manifest import generate_manifest, map_windows_assets
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


if __name__ == "__main__":
    unittest.main()
