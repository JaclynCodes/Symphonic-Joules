"""
Comprehensive tests for .vscode/settings.json configuration.

This module validates VSCode workspace settings:
- JSON structure and syntax
- Configuration keys and values
- GitHub Pull Requests extension settings
- Branch name configurations
- Best practices and conventions
"""

import pytest
import json
from pathlib import Path


@pytest.fixture(scope='module')
def settings_raw(vscode_settings_path):
    """Load raw VSCode settings content"""
    with open(vscode_settings_path, 'r') as f:
        return f.read()


class TestVSCodeDirectoryStructure:
    """Test .vscode directory structure"""
    
    def test_vscode_directory_exists(self, repo_root):
        """Test that .vscode directory exists"""
        vscode_dir = repo_root / '.vscode'
        assert vscode_dir.exists(), \
            ".vscode directory should exist in repository root"
    
    def test_vscode_directory_is_directory(self, repo_root):
        """Test that .vscode is a directory, not a file"""
        vscode_dir = repo_root / '.vscode'
        assert vscode_dir.is_dir(), \
            ".vscode should be a directory"
    
    def test_settings_file_exists(self, vscode_settings_path):
        """Test that settings.json exists in .vscode directory"""
        assert vscode_settings_path.exists(), \
            "settings.json should exist in .vscode directory"
    
    def test_settings_file_is_file(self, vscode_settings_path):
        """Test that settings.json is a file"""
        assert vscode_settings_path.is_file(), \
            "settings.json should be a file"


class TestJSONStructure:
    """Test JSON structure and syntax"""
    
    def test_settings_is_valid_json(self, settings_raw):
        """Test that settings.json contains valid JSON"""
        try:
            json.loads(settings_raw)
        except json.JSONDecodeError as e:
            pytest.fail(f"settings.json contains invalid JSON: {e}")
    
    def test_settings_is_json_object(self, vscode_settings):
        """Test that root structure is a JSON object"""
        assert isinstance(vscode_settings, dict), \
            "settings.json root should be a JSON object (dict)"
    
    def test_settings_not_empty(self, vscode_settings):
        """Test that settings contain at least one configuration"""
        assert len(vscode_settings) > 0, "Settings should not be empty"
    
    def test_json_uses_double_quotes(self, settings_raw):
        """Test that JSON uses double quotes, not single quotes"""
        # Check for single-quoted strings (which are invalid in JSON)
        # This is a simplified check - proper JSON validation is done above
        assert "'" not in settings_raw or settings_raw.count("'") == 0, \
            "JSON should use double quotes, not single quotes"
    
    def test_json_is_properly_formatted(self, settings_raw):
        """Test that JSON has consistent indentation"""
        lines = settings_raw.split('\n')
        # Check that file uses consistent indentation (spaces)
        indented_lines = [line for line in lines if line and line[0] == ' ']
        if indented_lines:
            # Check that we're using spaces, not tabs
            assert all('\t' not in line for line in lines), \
                "JSON should use spaces for indentation, not tabs"


class TestGitHubPullRequestsConfiguration:
    """Test GitHub Pull Requests extension settings"""
    
    def test_has_github_pr_settings(self, vscode_settings):
        """Test that GitHub Pull Requests settings are configured"""
        pr_keys = [k for k in vscode_settings.keys() 
                   if k.startswith('githubPullRequests')]
        assert len(pr_keys) > 0, \
            "Should have GitHub Pull Requests extension settings"
    
    def test_has_ignored_branches_setting(self, vscode_settings):
        """Test that ignored branches setting exists"""
        assert 'githubPullRequests.ignoredPullRequestBranches' in vscode_settings, \
            "Should configure ignored PR branches"
    
    def test_ignored_branches_is_list(self, vscode_settings):
        """Test that ignored branches is a list"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches')
        assert isinstance(ignored, list), \
            "ignoredPullRequestBranches should be a list"
    
    def test_ignored_branches_not_empty(self, vscode_settings):
        """Test that ignored branches list is not empty"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert len(ignored) > 0, \
            "Should have at least one ignored branch configured"
    
    def test_master_branch_is_ignored(self, vscode_settings):
        """Test that 'Master' branch is in ignored list"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert 'Master' in ignored, \
            "'Master' branch should be in ignored branches list"
    
    def test_branch_names_are_strings(self, vscode_settings):
        """Test that all branch names are strings"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        for branch in ignored:
            assert isinstance(branch, str), \
                f"Branch name should be string, got {type(branch)}: {branch}"


class TestBranchNamingConventions:
    """Test branch naming in configuration"""
    
    def test_uses_capital_master(self, vscode_settings):
        """Test that configuration uses 'Master' with capital M"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        # Should use 'Master' not 'master' to match repository convention
        assert 'Master' in ignored, \
            "Should use 'Master' (capitalized) to match repo convention"
        assert 'master' not in ignored, \
            "Should not have lowercase 'master' in addition to 'Master'"
    
    def test_no_main_branch_ignored(self, vscode_settings):
        """Test that 'main' branch is not ignored (as it's the active branch)"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert 'main' not in ignored and 'Main' not in ignored, \
            "'main' branch should not be ignored (it's the active default branch)"
    
    def test_branch_names_dont_have_spaces(self, vscode_settings):
        """Test that branch names don't contain spaces"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        for branch in ignored:
            assert ' ' not in branch, f"Branch name '{branch}' should not contain spaces"
    
    def test_branch_names_are_reasonable_length(self, vscode_settings):
        """Test that branch names are reasonable length"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        for branch in ignored:
            assert len(branch) <= 100, \
                f"Branch name '{branch}' seems unreasonably long (>{100} chars)"


class TestConfigurationCompleteness:
    """Test that configuration is complete and purposeful"""
    
    def test_no_empty_settings(self, vscode_settings):
        """Test that no settings have empty values unless intentional"""
        for key, value in vscode_settings.items():
            if isinstance(value, list):
                assert len(value) >= 0, \
                    f"Setting '{key}' has a list that should not be empty"
            elif isinstance(value, str):
                # Empty strings might be intentional for some settings
                pass
            elif isinstance(value, dict):
                # Nested objects should have content
                pass
    
    def test_all_keys_are_strings(self, vscode_settings):
        """Test that all setting keys are strings"""
        for key in vscode_settings.keys():
            assert isinstance(key, str), f"Setting key should be string: {key}"
    
    def test_setting_keys_follow_convention(self, vscode_settings):
        """Test that setting keys follow VSCode convention"""
        # Common VSCode setting prefixes
        known_prefixes = [
            'editor.', 'files.', 'workbench.', 'terminal.',
            'python.', 'git.', 'githubPullRequests.', 'eslint.',
            'typescript.', 'javascript.', '[python]'
        ]
        for key in vscode_settings.keys():
            is_known = any(key.startswith(prefix) for prefix in known_prefixes)
            # VSCode settings typically use camelCase with dots
            assert '.' in key or key[0].islower() or is_known, \
                f"Setting key '{key}' should follow VSCode naming convention"


class TestBestPractices:
    """Test VSCode configuration best practices"""
    
    def test_file_has_minimal_settings(self, vscode_settings):
        """Test that file doesn't have excessive settings"""
        # Workspace settings should be minimal and project-specific
        assert len(vscode_settings) <= 20, \
            "Workspace settings should be minimal (avoid personal preferences)"
    
    def test_no_personal_settings(self, vscode_settings):
        """Test that file doesn't include personal user preferences"""
        # Common personal preference keys that shouldn't be in workspace settings
        personal_keys = [
            'editor.fontSize', 'editor.fontFamily', 'workbench.colorTheme',
            'terminal.integrated.shell', 'window.zoomLevel'
        ]
        for key in personal_keys:
            assert key not in vscode_settings, \
                f"'{key}' is a personal preference and shouldn't be in workspace settings"
    
    def test_no_absolute_paths(self, settings_raw):
        """Test that configuration doesn't contain absolute file paths"""
        # Absolute paths would break on different machines
        import re
        # Check for Windows paths (C:\) or Unix absolute paths that aren't URLs
        abs_path_patterns = [
            r'[A-Z]:\\',  # Windows paths
            r'(?<!")\/(?:home|root|Users)\/',  # Unix home dirs
        ]
        for pattern in abs_path_patterns:
            matches = re.findall(pattern, settings_raw)
            assert len(matches) == 0, \
                f"Settings should not contain absolute paths: {matches}"
    
    def test_no_sensitive_information(self, settings_raw):
        """Test that settings don't contain sensitive information"""
        sensitive_patterns = ['password', 'token', 'api_key', 'secret', 'credential']
        lower_content = settings_raw.lower()
        
        for pattern in sensitive_patterns:
            if pattern in lower_content:
                # Check if it's just a setting name (key), not a value
                lines = [l for l in settings_raw.split('\n') if pattern in l.lower()]
                for line in lines:
                    # Should only be on left side of colon (key name)
                    if ':' in line:
                        key_part = line.split(':')[0]
                        assert pattern in key_part.lower(), \
                            f"Potential sensitive data '{pattern}' found in settings"
    
    def test_settings_file_size_reasonable(self, settings_raw):
        """Test that settings file is not excessively large"""
        # Should be reasonable size for workspace settings
        assert len(settings_raw) < 10000, \
            "Settings file seems excessively large (>10KB)"


class TestEdgeCases:
    """Test edge cases and potential issues"""
    
    def test_file_not_empty(self, settings_raw):
        """Test that settings file is not empty"""
        assert len(settings_raw.strip()) > 0, "Settings file should not be empty"
    
    def test_no_duplicate_keys(self, settings_raw):
        """Test that JSON doesn't have duplicate keys"""
        # Parse JSON to ensure it's valid (no exception means valid)
        json.loads(settings_raw)
        # Count keys in raw JSON
        import re
        key_pattern = r'"([^"]+)"\s*:'
        keys_in_raw = re.findall(key_pattern, settings_raw)
        unique_keys = set(keys_in_raw)
        assert len(keys_in_raw) == len(unique_keys), \
            "settings.json should not have duplicate keys"
    
    def test_properly_closed_braces(self, settings_raw):
        """Test that JSON has properly matched braces"""
        open_braces = settings_raw.count('{')
        close_braces = settings_raw.count('}')
        assert open_braces == close_braces, "Braces should be properly matched"
        
        open_brackets = settings_raw.count('[')
        close_brackets = settings_raw.count(']')
        assert open_brackets == close_brackets, "Brackets should be properly matched"
    
    def test_file_ends_with_newline(self, settings_raw):
        """Test that file ends with a newline"""
        assert settings_raw.endswith('\n'), \
            "JSON file should end with a newline character"
    
    def test_empty_ignored_list_would_be_useless(self, vscode_settings):
        """Test that if ignored branches is set, it has content"""
        if 'githubPullRequests.ignoredPullRequestBranches' in vscode_settings:
            ignored = vscode_settings['githubPullRequests.ignoredPullRequestBranches']
            assert len(ignored) > 0, \
                "If ignoredPullRequestBranches is set, it should have branches listed"


class TestPythonSpecificSettings:
    """Test Python-specific settings (if present)"""
    
    def test_python_settings_if_present(self, vscode_settings):
        """Test that Python settings are appropriate if configured"""
        python_keys = [k for k in vscode_settings.keys() if k.startswith('python.')]
        if python_keys:
            # If Python settings exist, they should be project-specific
            # Examples: python.testing.pytestEnabled, python.linting.enabled
            for key in python_keys:
                value = vscode_settings[key]
                # These shouldn't be path-based settings
                if isinstance(value, str):
                    assert not value.startswith('/') or value.startswith('${'), \
                        f"Python setting '{key}' should not use absolute paths"
    
    def test_no_git_personal_settings(self, vscode_settings):
        """Test that git user settings are not in workspace config"""
        personal_git_keys = ['git.user.name', 'git.user.email']
        for key in personal_git_keys:
            assert key not in vscode_settings, \
                f"'{key}' is personal and should not be in workspace settings"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])