"""
Unit tests for FLExProject class.

Author: FlexTools Development Team
"""

import unittest
import logging

logging.basicConfig(filename='flexlibs.log', filemode='w', level=logging.DEBUG)

from flexlibs import FLExInitialize, FLExCleanup
from flexlibs import FLExProject, AllProjectNames


class TestFLExProject(unittest.TestCase):
    """Test FLExProject functionality."""

    @classmethod
    def setUpClass(cls):
        """Initialize FLEx before running tests."""
        FLExInitialize()

    @classmethod
    def tearDownClass(cls):
        """Clean up FLEx after running tests."""
        FLExCleanup()

    def test_AllProjectNames(self):
        """Test that AllProjectNames returns a list."""
        self.assertIsInstance(AllProjectNames(), list)

    def test_OpenProject(self):
        """Test opening and closing a project."""
        fp = FLExProject()
        # Grab the first project in the list
        projectName = AllProjectNames()[0]
        try:
            fp.OpenProject(projectName, writeEnabled=False)
        except Exception as e:
            self.fail(f"Exception opening project {projectName}:\n{e}")
        fp.CloseProject()

    def test_ReadLexicon(self):
        """Test reading lexicon entries from a project."""
        fp = FLExProject()
        projectName = AllProjectNames()[0]
        try:
            fp.OpenProject(projectName, writeEnabled=False)
        except Exception as e:
            self.fail(f"Exception opening project {projectName}: {e}")

        # Traverse the whole lexicon
        for lexEntry in fp.LexiconAllEntries():
            self.assertIsInstance(fp.LexiconGetHeadword(lexEntry), str)

        fp.CloseProject()



if __name__ == "__main__":
    unittest.main()
