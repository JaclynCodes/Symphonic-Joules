"""
Shared pytest fixtures for workflow tests.

This module provides common fixtures used across workflow test files to reduce
code duplication and ensure consistency.
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope='module')
def get_workflow_path(repo_root):
    """
    Fixture that returns a function to get workflow file path.
    
    Usage:
        def workflow_path(get_workflow_path):
            return get_workflow_path('blank.yml')
    
    Args:
        filename: Name of the workflow file
    
    Returns:
        Path to the workflow file
    """
    def _get_path(filename):
        return repo_root / '.github' / 'workflows' / filename
    
    return _get_path


@pytest.fixture(scope='module')
def load_workflow_file(repo_root):
    """
    Fixture that returns a function to load any workflow file.
    
    Usage:
        def workflow_content(load_workflow_file):
            return load_workflow_file('blank.yml')
    
    Args:
        filename: Name of the workflow file
    
    Returns:
        Parsed YAML content of the workflow file
    """
    def _load_workflow(filename):
        workflow_path = repo_root / '.github' / 'workflows' / filename
        with open(workflow_path, 'r') as f:
            return yaml.safe_load(f)
    
    return _load_workflow
