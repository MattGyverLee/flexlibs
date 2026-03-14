#
#   conftest.py
#
#   Pytest configuration for contract tests.
#   Overrides the parent conftest's autouse FieldWorks initialization
#   so contract tests can run without pythonnet/FieldWorks.
#
#   Copyright 2025
#

import pytest


@pytest.fixture(scope="session", autouse=True)
def initialize_flex_for_tests():
    """
    Override parent conftest's autouse fixture.
    Contract tests do not require FieldWorks initialization.
    The static analysis tests run on pure Python AST parsing.
    """
    yield
