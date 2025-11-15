"""Test suite for documentation files"""
import pytest
import os
import re
from pathlib import Path

@pytest.fixture(scope='module')
def repo_root():
    return Path(__file__).parent.parent

class TestDocFiles:
    def test_readme_exists(self, repo_root):
        assert (repo_root / 'README.md').exists()
    
    def test_contributing_exists(self, repo_root):
        assert (repo_root / 'CONTRIBUTING.md').exists()
    
    def test_changelog_exists(self, repo_root):
        assert (repo_root / 'CHANGELOG.md').exists()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])