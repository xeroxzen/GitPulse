import unittest
from gitpulse.core.contributor import Contributor, ContributorStats

class TestContributor(unittest.TestCase):
    def setUp(self):
        self.contributor = Contributor("Test User", "test@example.com")
    
    def test_init(self):
        self.assertEqual(self.contributor.name, "Test User")
        self.assertEqual(self.contributor.email, "test@example.com")
        self.assertEqual(self.contributor.stats.commit_count, 0)
    
    def test_update_stats(self):
        self.contributor.update_stats(
            commit_count=5,
            lines_added=100,
            lines_deleted=50,
            files_changed=10,
            languages={"Python": 5, "JavaScript": 3}
        )
        
        self.assertEqual(self.contributor.stats.commit_count, 5)
        self.assertEqual(self.contributor.stats.lines_added, 100)
        self.assertEqual(self.contributor.stats.lines_deleted, 50)
        self.assertEqual(self.contributor.stats.files_changed, 10)
        self.assertEqual(self.contributor.stats.languages["Python"], 5)
        self.assertEqual(self.contributor.stats.languages["JavaScript"], 3)
    
    def test_total_changes(self):
        self.contributor.update_stats(lines_added=100, lines_deleted=50)
        self.assertEqual(self.contributor.stats.total_changes, 150)
    
    def test_calculate_percentage(self):
        self.contributor.update_stats(lines_added=100, lines_deleted=50)
        percentage = self.contributor.stats.calculate_percentage(500)
        self.assertEqual(percentage, 30.0)  # (150/500) * 100 = 30%
        self.assertEqual(self.contributor.stats.percentage, 30.0)

if __name__ == "__main__":
    unittest.main()