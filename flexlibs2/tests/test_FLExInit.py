"""
Unit tests for FLEx initialization and cleanup.

Author: FlexTools Development Team
"""

import unittest
from flexlibs2 import FLExInitialize, FLExCleanup


class TestFLExInit(unittest.TestCase):
    """Test FLEx initialization and cleanup functions."""

    def test_InitializeCleanup(self):
        """Test that FLEx can be initialized and cleaned up without errors."""
        try:
            FLExInitialize()
        except Exception as e:
            self.fail(f"Failed to initialize: {e}")
        try:
            FLExCleanup()
        except Exception as e:
            self.fail(f"Failed to cleanup: {e}")


if __name__ == "__main__":
    unittest.main()
