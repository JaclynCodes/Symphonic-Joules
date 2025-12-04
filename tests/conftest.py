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


@pytest.fixture(scope='module')
def dependabot_path():
    """Get path to dependabot configuration file."""
    return Path('.github/dependabot.yml')


@pytest.fixture(scope='module')
def tests_dir(repo_root):
    """Get the tests directory."""
    return repo_root / 'tests'


@pytest.fixture(scope='module')
def readme_path(repo_root):
    """Get the README.md path in tests directory."""
    return repo_root / 'tests' / 'README.md'
