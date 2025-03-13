import unittest
import tempfile
import os
import git
from pathlib import Path
from gitpulse.core.codebase import Codebase

class TestCodebase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory with a git repository
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_path = self.temp_dir.name
        
        # Initialize git repository
        repo = git.Repo.init(self.repo_path)
        
        # Create a test file
        test_file = Path(self.repo_path) / "test.py"
        with open(test_file, "w") as f:
            f.write("print('Hello, World!')")
        
        # Add and commit the file
        repo.git.add(all=True)
        repo.git.commit("-m", "Initial commit")
        
        # Create the Codebase instance
        self.codebase = Codebase(self.repo_path)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_get_basic_info(self):
        info = self.codebase.get_basic_info()
        self.assertEqual(info["name"], Path(self.repo_path).name)
        self.assertEqual(info["total_files"], 1)
    
    def test_get_language_stats(self):
        languages = self.codebase.get_language_stats()
        self.assertIn("Python", languages)
        self.assertEqual(languages["Python"], 1)
    
    def test_get_file_stats(self):
        stats = self.codebase.get_file_stats()
        self.assertEqual(stats["file_count"], 1)
        self.assertIn(".py", stats["by_extension"])
        self.assertEqual(stats["by_extension"][".py"], 1)

if __name__ == "__main__":
    unittest.main()