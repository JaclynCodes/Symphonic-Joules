"""
Shared pytest fixtures for the test suite.

This module provides common fixtures used across multiple test files to reduce
code duplication and ensure consistency.
"""

import pytest
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent
