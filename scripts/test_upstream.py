import unittest

from update_manifest import extract_github_repo


class TestUpstreamExtraction(unittest.TestCase):

    def test_extract_from_architecture(self):
        manifest = {
            "architecture": {
                "64bit": {
                    "url": "https://github.com/nicholaswilde/cook-docs/releases/download/v0.6.1/cook-docs_0.6.1_Windows_x86_64.tar.gz"
                }
            }
        }
        self.assertEqual(
            extract_github_repo(manifest), "nicholaswilde/cook-docs"
        )

    def test_extract_from_homepage(self):
        manifest = {
            "homepage": "https://github.com/nicholaswilde/tfa",
            "architecture": {},
        }
        self.assertEqual(extract_github_repo(manifest), "nicholaswilde/tfa")

    def test_extract_from_top_level_url(self):
        manifest = {
            "url": "https://github.com/nicholaswilde/enstow/releases/download/v0.1.0/enstow.zip"
        }
        self.assertEqual(extract_github_repo(manifest), "nicholaswilde/enstow")


if __name__ == "__main__":
    unittest.main()
