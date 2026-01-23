"""
Shared pytest fixtures for the test suite.

This module provides common fixtures used across multiple test files to reduce
code duplication and ensure consistency.

Performance optimizations:
- Cached file contents to eliminate redundant I/O operations
- Cached AST parsing to avoid repeated parsing of the same files
"""

import pytest
import json
import ast
from pathlib import Path


@pytest.fixture(scope='session')
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


@pytest.fixture(scope='module')
def vscode_settings_path(repo_root):
    """Get path to VSCode settings file."""
    return repo_root / '.vscode' / 'settings.json'


@pytest.fixture(scope='module')
def vscode_settings(vscode_settings_path):
    """Load and parse VSCode settings."""
    with open(vscode_settings_path, 'r') as f:
        return json.load(f)


@pytest.fixture(scope='module')
def faq_path(repo_root):
    """Get path to FAQ document."""
    return repo_root / 'docs' / 'faq.md'


@pytest.fixture(scope='module')
def installation_path(repo_root):
    """Get path to installation guide."""
    return repo_root / 'docs' / 'installation-setup.md'


@pytest.fixture(scope='session')
def test_file_contents_cache(repo_root):
    """
    Cache file contents for all test files to eliminate redundant I/O.
    
    This fixture reads all test files once at session start and caches
    their contents. This prevents multiple test methods from repeatedly
    opening and reading the same files.
    
    Returns:
        dict: Mapping of Path -> file content string
    """
    workflows_dir = repo_root / 'tests' / 'workflows'
    test_files = list(workflows_dir.glob('test_*.py'))
    
    cache = {}
    for test_file in test_files:
        with open(test_file, 'r') as f:
            cache[test_file] = f.read()
    
    return cache


@pytest.fixture(scope='session')
def test_file_ast_cache(test_file_contents_cache):
    """
    Cache AST parse trees for all test files to eliminate redundant parsing.
    
    This fixture parses each test file's AST once and caches the result.
    AST parsing is expensive and repeated parsing is a major performance
    bottleneck.
    
    Returns:
        dict: Mapping of Path -> ast.Module object
    """
    cache = {}
    for test_file, content in test_file_contents_cache.items():
        try:
            cache[test_file] = ast.parse(content)
        except SyntaxError:
            # If file has syntax errors, store None
            cache[test_file] = None
    
    return cache
