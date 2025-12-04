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


class TestVSCodeSettingsStructure:
    """Test VSCode settings structure"""
    
    def test_vscode_settings_file_exists(self, vscode_settings_path):
        """Test that .vscode/settings.json exists"""
        assert vscode_settings_path.exists(), \
            "VSCode settings file should exist"
    
    def test_vscode_directory_exists(self, repo_root):
        """Test that .vscode directory exists"""
        vscode_dir = repo_root / '.vscode'
        assert vscode_dir.exists(), \
            ".vscode directory should exist"
        assert vscode_dir.is_dir(), \
            ".vscode should be a directory"
    
    def test_settings_is_valid_json(self, vscode_settings):
        """Test that settings.json is valid JSON"""
        assert vscode_settings is not None, \
            "VSCode settings should not be None"
        assert isinstance(vscode_settings, dict), \
            "VSCode settings should be a dictionary"
    
    def test_settings_not_empty(self, vscode_settings):
        """Test that settings file is not empty"""
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
        """Test that ignored branches list is not empty"""
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
        """Test that JSON file ends with newline"""
        with open(vscode_settings_path, 'rb') as f:
            content = f.read()
            # Check if file ends with newline
            if len(content) > 0:
                # Allow either LF or CRLF
                assert content[-1:] in [b'\n', b'\r'], \
                    "JSON file should end with newline"
    
    def test_file_uses_consistent_indentation(self, vscode_settings_path):
        """Test that JSON uses consistent indentation"""
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
        """Test that settings file is reasonably sized"""
        file_size = vscode_settings_path.stat().st_size
        # Settings file should be less than 10KB for a simple config
        assert file_size < 10240, \
            "Settings file should be reasonably sized (< 10KB)"
    
    def test_no_sensitive_data_in_settings(self, vscode_settings):
        """Test that settings don't contain sensitive information"""
        settings_str = json.dumps(vscode_settings).lower()
        sensitive_keywords = ['password', 'token', 'secret', 'api_key', 'apikey']
        
        for keyword in sensitive_keywords:
            assert keyword not in settings_str, \
                f"Settings should not contain sensitive data: {keyword}"
    
    def test_settings_work_with_git(self, repo_root):
        """Test that .vscode directory is properly tracked"""
        gitignore_path = repo_root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore = f.read()
                # .vscode/ should not be completely ignored
                assert '.vscode/' not in gitignore or '!.vscode/settings.json' in gitignore, \
                    ".vscode/settings.json should be trackable by git"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])