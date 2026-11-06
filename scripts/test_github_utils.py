import os
import tempfile
import unittest

from github_utils import create_github_request, get_github_token, load_env_file


class TestGitHubUtils(unittest.TestCase):

    def setUp(self):
        self.orig_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.orig_env)

    def test_no_token_set(self):
        os.environ.pop("GITHUB_TOKEN", None)
        os.environ.pop("GH_TOKEN", None)
        token = get_github_token(env_file="nonexistent.env")
        self.assertIsNone(token)
        req = create_github_request("https://api.github.com", token=token)
        self.assertNotIn("Authorization", req.headers)
        self.assertEqual(
            req.headers.get("User-agent"), "Gemini-CLI-Scoop-Updater"
        )

    def test_env_var_token(self):
        os.environ.pop("GITHUB_TOKEN", None)
        os.environ["GH_TOKEN"] = "env_var_gh_token"
        token = get_github_token(env_file="nonexistent.env")
        self.assertEqual(token, "env_var_gh_token")
        req = create_github_request("https://api.github.com", token=token)
        self.assertEqual(
            req.headers.get("Authorization"), "Bearer env_var_gh_token"
        )

    def test_dotenv_file_takes_precedence(self):
        os.environ["GITHUB_TOKEN"] = "system_env_token"
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write("GITHUB_TOKEN=dotenv_token\n")
            temp_path = f.name
        try:
            token = get_github_token(env_file=temp_path)
            self.assertEqual(token, "dotenv_token")
            req = create_github_request("https://api.github.com", token=token)
            self.assertEqual(
                req.headers.get("Authorization"), "Bearer dotenv_token"
            )
        finally:
            os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
