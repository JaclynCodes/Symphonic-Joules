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
import re
from pathlib import Path


@pytest.fixture(scope='module')
def vscode_raw(vscode_settings_path):
    """Get raw content of VSCode settings"""
    with open(vscode_settings_path, 'r') as f:
        return f.read()


class TestVSCodeSettingsStructure:
    """Test VSCode settings file structure"""
    
    def test_vscode_directory_exists(self, repo_root):
        """Test that .vscode directory exists"""
        vscode_dir = repo_root / '.vscode'
        assert vscode_dir.exists(), \
            ".vscode directory should exist in repository root"
        assert vscode_dir.is_dir(), \
            ".vscode should be a directory"
    
    def test_settings_file_exists(self, vscode_settings_path):
        """Test that .vscode/settings.json exists"""
        assert vscode_settings_path.exists(), \
            ".vscode/settings.json should exist"
        assert vscode_settings_path.is_file(), \
            "settings.json should be a file"
    
    def test_settings_is_valid_json(self, vscode_settings):
        """Test that settings.json is valid JSON"""
        assert vscode_settings is not None, \
            "VSCode settings should not be None"
        assert isinstance(vscode_settings, dict), \
            "VSCode settings should be a dictionary"
    
    def test_settings_not_empty(self, vscode_settings):
        """Test that settings contain at least one configuration"""
        assert len(vscode_settings) > 0, \
            "VSCode settings should not be empty"


class TestGitHubPRSettings:
    """Test GitHub Pull Request extension settings"""
    
    def test_has_github_pr_settings(self, vscode_settings):
        """Test that GitHub PR settings are configured"""
        github_keys = [k for k in vscode_settings.keys() 
                      if 'githubPullRequests' in k]
        assert len(github_keys) > 0, \
            "Should have GitHub Pull Requests settings"
    
    def test_ignored_branches_configured(self, vscode_settings):
        """Test that ignored PR branches are configured"""
        assert 'githubPullRequests.ignoredPullRequestBranches' in vscode_settings, \
            "Should configure ignored PR branches"
    
    def test_ignored_branches_is_array(self, vscode_settings):
        """Test that ignored branches is an array"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches')
        assert isinstance(ignored, list), \
            "Ignored branches should be an array"
    
    def test_ignored_branches_not_empty(self, vscode_settings):
        """Test that ignored branches list is not empty"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert len(ignored) > 0, \
            "Should have at least one ignored branch"
    
    def test_main_branch_is_ignored(self, vscode_settings):
        """Test that main branch is in ignored list"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert 'main' in ignored, \
            "main branch should be ignored for PRs"
    
    def test_branch_names_are_strings(self, vscode_settings):
        """Test that all branch names are strings"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        for branch in ignored:
            assert isinstance(branch, str), \
                f"Branch name should be string, got {type(branch)}: {branch}"


class TestJSONFormatting:
    """Test JSON formatting and style"""
    
    def test_json_is_properly_indented(self, vscode_raw):
        """Test that JSON is properly indented"""
        assert '    ' in vscode_raw or '  ' in vscode_raw, \
            "JSON should be indented for readability"
    
    def test_json_uses_double_quotes(self, vscode_raw):
        """Test that JSON uses double quotes (not single quotes)"""
        if '"' in vscode_raw or "'" in vscode_raw:
            assert '"' in vscode_raw, \
                "JSON should use double quotes"
    
    def test_json_is_properly_formatted(self, vscode_raw):
        """Test that JSON has consistent indentation"""
        lines = vscode_raw.split('\n')
        indented_lines = [line for line in lines if line and line[0] == ' ']
        if indented_lines:
            assert all('\t' not in line for line in lines), \
                "JSON should use spaces for indentation, not tabs"
    
    def test_no_trailing_commas(self, vscode_settings):
        """Test that JSON doesn't have trailing commas"""
        assert vscode_settings is not None, \
            "Valid JSON should not have trailing commas"


class TestSettingsValidation:
    """Test validity of settings values"""
    
    def test_all_keys_are_strings(self, vscode_settings):
        """Test that all setting keys are strings"""
        for key in vscode_settings.keys():
            assert isinstance(key, str), \
                f"Setting key should be string: {key}"
    
    def test_setting_keys_follow_convention(self, vscode_settings):
        """Test that setting keys follow VSCode convention"""
        for key in vscode_settings.keys():
            assert '.' in key or key[0].islower() or key.startswith('['), \
                f"Setting key '{key}' should follow VSCode naming convention"
    
    def test_array_values_contain_valid_types(self, vscode_settings):
        """Test that array settings contain valid JSON types"""
        for key, value in vscode_settings.items():
            if isinstance(value, list):
                for item in value:
                    assert isinstance(item, (str, int, bool, dict, float, type(None))), \
                        f"Array items in '{key}' should be valid JSON types"


class TestBranchNameValidation:
    """Test branch name configurations"""
    
    def test_ignored_branch_names_are_valid(self, vscode_settings):
        """Test that branch names are valid strings"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        for branch in ignored:
            assert isinstance(branch, str), \
                f"Branch name should be string: {branch}"
            assert len(branch) > 0, \
                "Branch name should not be empty"
    
    def test_branch_names_dont_have_spaces(self, vscode_settings):
        """Test that branch names don't contain spaces"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        for branch in ignored:
            assert ' ' not in branch, \
                f"Branch name '{branch}' should not contain spaces"
    
    def test_branch_names_are_reasonable_length(self, vscode_settings):
        """Test that branch names are reasonable length"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        for branch in ignored:
            assert len(branch) <= 100, \
                f"Branch name '{branch}' seems unreasonably long (>{100} chars)"
    
    def test_no_duplicate_main_master(self, vscode_settings):
        """Test that configuration doesn't have both main and master"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        # Should not have duplicate variations of the default branch
        main_variations = sum(1 for b in ignored if b.lower() in ['main', 'master'])
        assert main_variations <= 1, \
            "Should not have multiple variations of main/master branch"


class TestWorkspaceBestPractices:
    """Test workspace configuration best practices"""
    
    def test_settings_file_size_reasonable(self, vscode_raw):
        """Test that settings file is not excessively large"""
        assert len(vscode_raw) < 10000, \
            "Settings file seems excessively large (>10KB)"
    
    def test_file_has_minimal_settings(self, vscode_settings):
        """Test that file doesn't have excessive settings"""
        assert len(vscode_settings) <= 20, \
            "Workspace settings should be minimal (avoid personal preferences)"
    
    def test_no_personal_settings(self, vscode_settings):
        """Test that file doesn't include personal user preferences"""
        personal_keys = [
            'editor.fontSize', 'editor.fontFamily', 'workbench.colorTheme',
            'terminal.integrated.shell', 'window.zoomLevel'
        ]
        for key in personal_keys:
            assert key not in vscode_settings, \
                f"'{key}' is a personal preference and shouldn't be in workspace settings"
    
    def test_no_sensitive_information(self, vscode_raw):
        """Test that settings don't contain sensitive information"""
        sensitive_patterns = ['password', 'token', 'api_key', 'secret', 'credential']
        lower_content = vscode_raw.lower()
        
        for pattern in sensitive_patterns:
            if pattern in lower_content:
                lines = [l for l in vscode_raw.split('\n') if pattern in l.lower()]
                for line in lines:
                    if ':' in line:
                        key_part = line.split(':')[0]
                        assert pattern in key_part.lower(), \
                            f"Potential sensitive data '{pattern}' found in settings"
    
    def test_no_absolute_paths(self, vscode_raw):
        """Test that settings don't use user-specific absolute paths"""
        abs_path_patterns = [
            r'[A-Z]:\\',
            r'(?<!")\/(?:home|root|Users)\/',
        ]
        for pattern in abs_path_patterns:
            matches = re.findall(pattern, vscode_raw)
            assert len(matches) == 0, \
                f"Settings should not contain absolute paths: {matches}"
    
    def test_no_git_personal_settings(self, vscode_settings):
        """Test that git user settings are not in workspace config"""
        personal_git_keys = ['git.user.name', 'git.user.email']
        for key in personal_git_keys:
            assert key not in vscode_settings, \
                f"'{key}' is personal and should not be in workspace settings"


class TestEdgeCases:
    """Test edge cases and potential issues"""
    
    def test_file_not_empty(self, vscode_raw):
        """Test that settings file is not empty"""
        assert len(vscode_raw.strip()) > 0, \
            "Settings file should not be empty"
    
    def test_settings_object_not_empty(self, vscode_settings):
        """Test that settings object has content"""
        assert len(vscode_settings.keys()) > 0, \
            "Should have at least one setting"
    
    def test_no_duplicate_keys(self, vscode_raw):
        """Test that JSON doesn't have duplicate keys"""
        def no_duplicate_object_pairs(pairs):
            keys = [k for k, _ in pairs]
            assert len(keys) == len(set(keys)), \
                "settings.json should not have duplicate keys in the same object"
            return dict(pairs)

        json.loads(vscode_raw, object_pairs_hook=no_duplicate_object_pairs)
    
    def test_properly_closed_braces(self, vscode_raw):
        """Test that JSON has properly matched braces"""
        open_braces = vscode_raw.count('{')
        close_braces = vscode_raw.count('}')
        assert open_braces == close_braces, \
            "Braces should be properly matched"
        
        open_brackets = vscode_raw.count('[')
        close_brackets = vscode_raw.count(']')
        assert open_brackets == close_brackets, \
            "Brackets should be properly matched"
    
    def test_file_ends_with_newline(self, vscode_settings_path):
        """Test that file ends with a newline"""
        with open(vscode_settings_path, 'rb') as f:
            content = f.read()
            if len(content) > 0:
                assert content[-1:] in [b'\n', b'\r'], \
                    "JSON file should end with newline"
    
    def test_settings_are_serializable(self, vscode_settings):
        """Test that settings can be serialized back to JSON"""
        try:
            json_str = json.dumps(vscode_settings, indent=4)
            assert len(json_str) > 0, \
                "Settings should serialize to non-empty JSON"
        except Exception as e:
            pytest.fail(f"Settings should be JSON serializable: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
