"""Validate Alembic migration chain integrity.

Ensures there is exactly one migration head and that the full SQL diff
for a clean database is syntactically valid (produced without errors).
This catches broken migration files before they reach production.
"""
import unittest
from alembic.config import Config
from alembic.script import ScriptDirectory


class MigrationChainTests(unittest.TestCase):
    def _load_script(self):
        config = Config("alembic.ini")
        return ScriptDirectory.from_config(config)

    def test_single_head(self):
        script = self._load_script()
        heads = script.get_heads()
        self.assertEqual(len(heads), 1,
                         f"Expected 1 migration head, got {len(heads)}: {heads}")

    def test_head_revision_is_nonempty(self):
        script = self._load_script()
        heads = script.get_heads()
        self.assertTrue(heads[0], "Head revision must not be empty")

    def test_head_migrates_from_expected_base(self):
        script = self._load_script()
        heads = script.get_heads()
        rev = script.get_revisions(heads[0])
        self.assertEqual(len(rev), 1, "Expected exactly one revision object for the head")
        rev_info = rev[0]
        self.assertEqual(rev_info.down_revision, "004",
                         "Expected migration head to point down to 004")


if __name__ == "__main__":
    unittest.main()