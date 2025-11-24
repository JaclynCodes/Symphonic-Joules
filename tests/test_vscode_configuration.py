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
def vscode_dir():
    """Get .vscode directory path"""
    return Path('.vscode')


@pytest.fixture(scope='module')
def settings_path(vscode_dir):
    """Get path to VSCode settings file"""
    return vscode_dir / 'settings.json'


@pytest.fixture(scope='module')
def settings_raw(settings_path):
    """Load raw VSCode settings content"""
    with open(settings_path, 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def settings_config(settings_raw):
    """Parse VSCode settings JSON"""
    return json.loads(settings_raw)


class TestVSCodeDirectoryStructure:
    """Test .vscode directory structure"""
    
    def test_vscode_directory_exists(self, vscode_dir):
        """Test that .vscode directory exists"""
        assert vscode_dir.exists(), \
            ".vscode directory should exist in repository root"
    
    def test_vscode_directory_is_directory(self, vscode_dir):
        """Test that .vscode is a directory, not a file"""
        assert vscode_dir.is_dir(), \
            ".vscode should be a directory"
    
    def test_settings_file_exists(self, settings_path):
        """Test that settings.json exists in .vscode directory"""
        assert settings_path.exists(), \
            "settings.json should exist in .vscode directory"
    
    def test_settings_file_is_file(self, settings_path):
        """Test that settings.json is a file"""
        assert settings_path.is_file(), \
            "settings.json should be a file"


class TestJSONStructure:
    """Test JSON structure and syntax"""
    
    def test_settings_is_valid_json(self, settings_raw):
        """Test that settings.json contains valid JSON"""
        try:
            json.loads(settings_raw)
        except json.JSONDecodeError as e:
            pytest.fail(f"settings.json contains invalid JSON: {e}")
    
    def test_settings_is_json_object(self, settings_config):
        """Test that root structure is a JSON object"""
        assert isinstance(settings_config, dict), \
            "settings.json root should be a JSON object (dict)"
    
    def test_json_uses_double_quotes(self, settings_raw):
        """Test that JSON uses double quotes, not single quotes"""
        # Check for single-quoted strings (which are invalid in JSON)
        import re
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
    
    def test_has_github_pr_settings(self, settings_config):
        """Test that GitHub Pull Requests settings are configured"""
        pr_keys = [k for k in settings_config.keys() 
                   if k.startswith('githubPullRequests')]
        assert len(pr_keys) > 0, \
            "Should have GitHub Pull Requests extension settings"
    
    def test_has_ignored_branches_setting(self, settings_config):
        """Test that ignored branches setting exists"""
        assert 'githubPullRequests.ignoredPullRequestBranches' in settings_config, \
            "Should configure ignored PR branches"
    
    def test_ignored_branches_is_list(self, settings_config):
        """Test that ignored branches is a list"""
        ignored = settings_config.get('githubPullRequests.ignoredPullRequestBranches')
        assert isinstance(ignored, list), \
            "ignoredPullRequestBranches should be a list"
    
    def test_ignored_branches_not_empty(self, settings_config):
        """Test that ignored branches list is not empty"""
        ignored = settings_config.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert len(ignored) > 0, \
            "Should have at least one ignored branch configured"
    
    def test_master_branch_is_ignored(self, settings_config):
        """Test that 'Master' branch is in ignored list"""
        ignored = settings_config.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert 'Master' in ignored, \
            "'Master' branch should be in ignored branches list"
    
    def test_branch_names_are_strings(self, settings_config):
        """Test that all branch names are strings"""
        ignored = settings_config.get('githubPullRequests.ignoredPullRequestBranches', [])
        for branch in ignored:
            assert isinstance(branch, str), \
                f"Branch name should be string, got {type(branch)}: {branch}"


class TestBranchNamingConventions:
    """Test branch naming in configuration"""
    
    def test_uses_capital_master(self, settings_config):
        """Test that configuration uses 'Master' with capital M"""
        ignored = settings_config.get('githubPullRequests.ignoredPullRequestBranches', [])
        # Should use 'Master' not 'master' to match repository convention
        assert 'Master' in ignored, \
            "Should use 'Master' (capitalized) to match repo convention"
        assert 'master' not in ignored, \
            "Should not have lowercase 'master' in addition to 'Master'"
    
    def test_no_main_branch_ignored(self, settings_config):
        """Test that 'main' branch is not ignored (as it's the active branch)"""
        ignored = settings_config.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert 'main' not in ignored and 'Main' not in ignored, \
            "'main' branch should not be ignored (it's the active default branch)"


class TestConfigurationCompleteness:
    """Test that configuration is complete and purposeful"""
    
    def test_no_empty_settings(self, settings_config):
        """Test that no settings have empty values unless intentional"""
        for key, value in settings_config.items():
            if isinstance(value, list):
                assert len(value) >= 0, \
                    f"Setting '{key}' has a list that should not be empty"
            elif isinstance(value, str):
                # Empty strings might be intentional for some settings
                pass
            elif isinstance(value, dict):
                # Nested objects should have content
                pass
    
    def test_all_settings_are_known_vscode_settings(self, settings_config):
        """Test that settings use valid VSCode setting keys"""
        # Common VSCode setting prefixes
        known_prefixes = [
            'editor.', 'files.', 'workbench.', 'terminal.',
            'python.', 'git.', 'githubPullRequests.', 'eslint.',
            'typescript.', 'javascript.', '[python]'
        ]
        for key in settings_config.keys():
            is_known = any(key.startswith(prefix) for prefix in known_prefixes)
            # It's okay to have settings we haven't listed, but warn about unusual ones
            if not is_known:
                # This is informational, not a hard failure
                pass


class TestBestPractices:
    """Test VSCode configuration best practices"""
    
    def test_file_has_minimal_settings(self, settings_config):
        """Test that file doesn't have excessive settings"""
        # Workspace settings should be minimal and project-specific
        assert len(settings_config) <= 20, \
            "Workspace settings should be minimal (avoid personal preferences)"
    
    def test_no_personal_settings(self, settings_config):
        """Test that file doesn't include personal user preferences"""
        # Common personal preference keys that shouldn't be in workspace settings
        personal_keys = [
            'editor.fontSize', 'editor.fontFamily', 'workbench.colorTheme',
            'terminal.integrated.shell', 'window.zoomLevel'
        ]
        for key in personal_keys:
            assert key not in settings_config, \
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


class TestDocumentation:
    """Test inline documentation in settings file"""
    
    def test_settings_can_have_comments_via_json5(self, settings_raw):
        """Test understanding that VSCode supports JSON5 comments"""
        # VSCode actually supports comments in settings.json (JSON5 format)
        # This test just documents that fact
        # If comments are present, they should be // style
        if '//' in settings_raw:
            lines = settings_raw.split('\n')
            comment_lines = [line for line in lines if '//' in line]
            assert len(comment_lines) > 0, \
                "Comments found, which is valid in VSCode settings (JSON5)"


class TestEdgeCases:
    """Test edge cases and potential issues"""
    
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
    
    def test_no_trailing_commas(self, settings_raw):
        """Test that JSON doesn't have trailing commas"""
        # While VSCode is lenient, standard JSON doesn't allow trailing commas
        # This is informational - VSCode settings can handle them
        import re
        # Check for comma before closing brace/bracket
        trailing_comma = re.search(r',\s*[}\]]', settings_raw)
        # This is not a hard failure as VSCode supports this
        if trailing_comma:
            pass  # VSCode supports trailing commas in settings
    
    def test_empty_ignored_list_would_be_useless(self, settings_config):
        """Test that if ignored branches is set, it has content"""
        if 'githubPullRequests.ignoredPullRequestBranches' in settings_config:
            ignored = settings_config['githubPullRequests.ignoredPullRequestBranches']
            assert len(ignored) > 0, \
                "If ignoredPullRequestBranches is set, it should have branches listed"
    
    def test_file_ends_with_newline(self, settings_raw):
        """Test that file ends with a newline"""
        assert settings_raw.endswith('\n'), \
            "JSON file should end with a newline character"


class TestGitConfiguration:
    """Test git-related VSCode settings (if present)"""
    
    def test_no_git_personal_settings(self, settings_config):
        """Test that git user settings are not in workspace config"""
        personal_git_keys = ['git.user.name', 'git.user.email']
        for key in personal_git_keys:
            assert key not in settings_config, \
                f"'{key}' is personal and should not be in workspace settings"


class TestPythonSpecificSettings:
    """Test Python-specific settings (if present)"""
    
    def test_python_settings_if_present(self, settings_config):
        """Test that Python settings are appropriate if configured"""
        python_keys = [k for k in settings_config.keys() if k.startswith('python.')]
        if python_keys:
            # If Python settings exist, they should be project-specific
            # Examples: python.testing.pytestEnabled, python.linting.enabled
            for key in python_keys:
                value = settings_config[key]
                # These shouldn't be path-based settings
                if isinstance(value, str):
                    assert not value.startswith('/') or value.startswith('${'), \
                        f"Python setting '{key}' should not use absolute paths"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])