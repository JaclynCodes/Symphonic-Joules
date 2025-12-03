"""
Tests for .vscode/settings.json

This module validates the VSCode workspace settings:
- JSON structure and syntax
- Settings validity
- Workspace configuration
- GitHub Pull Requests settings
"""

import pytest
import json
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """
    Locate the repository root directory.
    
    Returns:
        Path: Path object pointing to the repository root (two levels up from this file).
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def vscode_settings_path(repo_root):
    """
    Return the Path to the repository's VSCode settings.json file.
    
    Parameters:
        repo_root (Path | str): Repository root directory.
    
    Returns:
        Path: Path to '.vscode/settings.json' inside the provided repository root.
    """
    return repo_root / '.vscode' / 'settings.json'


@pytest.fixture(scope='module')
def vscode_settings(vscode_settings_path):
    """
    Load VSCode workspace settings from the given file path.
    
    Parameters:
        vscode_settings_path (str | pathlib.Path): Path to the `.vscode/settings.json` file to read.
    
    Returns:
        dict: Parsed JSON content of the VSCode settings file.
    """
    with open(vscode_settings_path, 'r') as f:
        return json.load(f)


class TestVSCodeSettingsStructure:
    """Test VSCode settings structure"""
    
    def test_vscode_settings_file_exists(self, vscode_settings_path):
        """Test that .vscode/settings.json exists"""
        assert vscode_settings_path.exists(), \
            "VSCode settings file should exist"
    
    def test_vscode_directory_exists(self, repo_root):
        """
        Verify that the repository contains a .vscode directory.
        """
        vscode_dir = repo_root / '.vscode'
        assert vscode_dir.exists(), \
            ".vscode directory should exist"
        assert vscode_dir.is_dir(), \
            ".vscode should be a directory"
    
    def test_settings_is_valid_json(self, vscode_settings):
        """
        Verify the VSCode settings file loads as a non-null dictionary.
        
        Asserts that the provided `vscode_settings` fixture is not None and is an instance of `dict`.
        """
        assert vscode_settings is not None, \
            "VSCode settings should not be None"
        assert isinstance(vscode_settings, dict), \
            "VSCode settings should be a dictionary"
    
    def test_settings_not_empty(self, vscode_settings):
        """
        Assert the parsed VSCode settings contain at least one top-level entry.
        """
        assert len(vscode_settings) > 0, \
            "VSCode settings should not be empty"


class TestGitHubPullRequestsSettings:
    """Test GitHub Pull Requests extension settings"""
    
    def test_has_ignored_branches_setting(self, vscode_settings):
        """Test that ignoredPullRequestBranches is configured"""
        assert 'githubPullRequests.ignoredPullRequestBranches' in vscode_settings, \
            "Should have ignoredPullRequestBranches setting"
    
    def test_ignored_branches_is_list(self, vscode_settings):
        """Test that ignoredPullRequestBranches is a list"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches')
        assert isinstance(ignored, list), \
            "ignoredPullRequestBranches should be a list"
    
    def test_master_branch_is_ignored(self, vscode_settings):
        """Test that Master branch is in ignored list"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert 'Master' in ignored, \
            "Master branch should be ignored for PRs"
    
    def test_ignored_branches_not_empty(self, vscode_settings):
        """
        Ensure the `githubPullRequests.ignoredPullRequestBranches` setting contains at least one entry.
        """
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert len(ignored) > 0, \
            "Should have at least one ignored branch"


class TestSettingsValidity:
    """Test that settings are valid and follow best practices"""
    
    def test_settings_keys_are_valid_format(self, vscode_settings):
        """Test that setting keys follow VSCode naming convention"""
        for key in vscode_settings.keys():
            # VSCode settings typically use camelCase or extension.setting format
            assert '.' in key or key[0].islower(), \
                f"Setting key '{key}' should follow VSCode naming convention"
    
    def test_no_workspace_specific_paths(self, vscode_settings):
        """Test that settings don't contain user-specific paths"""
        settings_str = json.dumps(vscode_settings)
        # Check for common user-specific paths
        forbidden_patterns = ['/Users/', 'C:\\Users\\', '/home/']
        for pattern in forbidden_patterns:
            assert pattern not in settings_str, \
                f"Settings should not contain user-specific path: {pattern}"
    
    def test_settings_are_serializable(self, vscode_settings):
        """Test that settings can be serialized back to JSON"""
        try:
            json_str = json.dumps(vscode_settings, indent=4)
            assert len(json_str) > 0, \
                "Settings should serialize to non-empty JSON"
        except Exception as e:
            pytest.fail(f"Settings should be JSON serializable: {e}")


class TestFileFormat:
    """Test JSON file formatting"""
    
    def test_file_ends_with_newline(self, vscode_settings_path):
        """
        Check that the VSCode settings JSON file ends with a newline character.
        
        Accepts either LF or CRLF as the terminating newline. Empty files are ignored.
        """
        with open(vscode_settings_path, 'rb') as f:
            content = f.read()
            # Check if file ends with newline
            if len(content) > 0:
                # Allow either LF or CRLF
                assert content[-1:] in [b'\n', b'\r'], \
                    "JSON file should end with newline"
    
    def test_file_uses_consistent_indentation(self, vscode_settings_path):
        """
        Assert that .vscode/settings.json uses a single, consistent indentation unit.
        
        Reads the file and verifies that the number of leading spaces on each indented line is a multiple of the smallest observed indentation, ensuring consistent indentation spacing.
        
        Parameters:
        	vscode_settings_path (Path): Path to the .vscode/settings.json file to check.
        """
        with open(vscode_settings_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            # Count spaces at start of indented lines
            indentations = []
            for line in lines:
                if line.strip() and line[0] == ' ':
                    indent_count = len(line) - len(line.lstrip(' '))
                    if indent_count > 0:
                        indentations.append(indent_count)
            
            if len(indentations) > 0:
                # Check that all indentations are multiples of the smallest
                min_indent = min(indentations)
                for indent in indentations:
                    assert indent % min_indent == 0, \
                        "JSON should use consistent indentation"


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_settings_file_is_not_too_large(self, vscode_settings_path):
        """
        Assert the VS Code settings.json file is smaller than 10 KB.
        
        Parameters:
            vscode_settings_path (Path): Path to the .vscode/settings.json file.
        
        Notes:
            The test fails if the file size is 10,240 bytes or larger.
        """
        file_size = vscode_settings_path.stat().st_size
        # Settings file should be less than 10KB for a simple config
        assert file_size < 10240, \
            "Settings file should be reasonably sized (< 10KB)"
    
    def test_no_sensitive_data_in_settings(self, vscode_settings):
        """
        Ensure VSCode settings do not contain common sensitive keywords.
        
        Checks the JSON-serialized settings for the presence of `password`, `token`, `secret`, `api_key`, and `apikey` (case-insensitive) and fails the test if any are found.
        """
        settings_str = json.dumps(vscode_settings).lower()
        sensitive_keywords = ['password', 'token', 'secret', 'api_key', 'apikey']
        
        for keyword in sensitive_keywords:
            assert keyword not in settings_str, \
                f"Settings should not contain sensitive data: {keyword}"
    
    def test_settings_work_with_git(self, repo_root):
        """
        Ensure the repository allows tracking of .vscode/settings.json in Git.
        
        Checks .gitignore (if present) to confirm that the `.vscode/` directory is not wholly ignored or that an explicit exception for `!.vscode/settings.json` exists.
        """
        gitignore_path = repo_root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore = f.read()
                # .vscode/ should not be completely ignored
                assert '.vscode/' not in gitignore or '!.vscode/settings.json' in gitignore, \
                    ".vscode/settings.json should be trackable by git"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])