"""
Tests for .vscode/settings.json configuration

This module validates the VSCode workspace settings:
- JSON structure and syntax validation
- Configuration options correctness
- GitHub PR settings validation
- Best practices for workspace settings
"""

import pytest
import json
from pathlib import Path


@pytest.fixture(scope='module')
def vscode_settings_path():
    """
    Return the path to the VS Code workspace settings file.
    
    Returns:
        Path: Path to the '.vscode/settings.json' file relative to the current working directory.
    """
    return Path('.vscode/settings.json')


@pytest.fixture(scope='module')
def vscode_settings(vscode_settings_path):
    """
    Load and parse the VS Code settings.json file into a Python object.
    
    Parameters:
        vscode_settings_path (str | pathlib.Path): Path to the `.vscode/settings.json` file.
    
    Returns:
        dict: Parsed JSON object representing the VS Code settings.
    """
    with open(vscode_settings_path, 'r') as f:
        return json.load(f)


@pytest.fixture(scope='module')
def vscode_raw(vscode_settings_path):
    """
    Read the raw contents of the VS Code settings file.
    
    Parameters:
        vscode_settings_path (str | pathlib.Path): Path to the `.vscode/settings.json` file.
    
    Returns:
        str: The file contents as a raw string, including whitespace and formatting.
    """
    with open(vscode_settings_path, 'r') as f:
        return f.read()


class TestVSCodeSettingsStructure:
    """Test VSCode settings file structure"""
    
    def test_settings_file_exists(self, vscode_settings_path):
        """Test that .vscode/settings.json exists"""
        assert vscode_settings_path.exists(), ".vscode/settings.json should exist"
    
    def test_settings_is_valid_json(self, vscode_settings):
        """Test that settings.json is valid JSON"""
        assert vscode_settings is not None, "Should parse as valid JSON"
        assert isinstance(vscode_settings, dict), "Settings should be a JSON object"
    
    def test_settings_not_empty(self, vscode_settings):
        """Test that settings contain at least one configuration"""
        assert len(vscode_settings) > 0, "Settings should not be empty"


class TestGitHubPRSettings:
    """Test GitHub Pull Request extension settings"""
    
    def test_has_github_pr_settings(self, vscode_settings):
        """Test that GitHub PR settings are configured"""
        # Check for any GitHub PR related settings
        github_keys = [k for k in vscode_settings.keys() if 'githubPullRequests' in k]
        assert len(github_keys) > 0, "Should have GitHub Pull Requests settings"
    
    def test_ignored_branches_configured(self, vscode_settings):
        """Test that ignored PR branches are configured"""
        assert 'githubPullRequests.ignoredPullRequestBranches' in vscode_settings, \
            "Should configure ignored PR branches"
    
    def test_ignored_branches_is_array(self, vscode_settings):
        """Test that ignored branches is an array"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches')
        assert isinstance(ignored, list), "Ignored branches should be an array"
    
    def test_ignored_branches_not_empty(self, vscode_settings):
        """Test that ignored branches list is not empty"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert len(ignored) > 0, "Should have at least one ignored branch"
    
    def test_master_branch_is_ignored(self, vscode_settings):
        """Test that Master branch is in ignored list"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        assert 'Master' in ignored, "Master branch should be ignored for PRs"


class TestJSONFormatting:
    """Test JSON formatting and style"""
    
    def test_json_is_properly_indented(self, vscode_raw):
        """Test that JSON is properly indented"""
        # Check if it has indentation (not minified)
        assert '    ' in vscode_raw or '  ' in vscode_raw, \
            "JSON should be indented for readability"
    
    def test_json_uses_double_quotes(self, vscode_raw):
        """Test that JSON uses double quotes (not single quotes)"""
        # JSON spec requires double quotes
        # If there are quotes, they should be double
        if '"' in vscode_raw or "'" in vscode_raw:
            assert '"' in vscode_raw, "JSON should use double quotes"
    
    def test_no_trailing_commas(self, vscode_settings):
        """Test that JSON doesn't have trailing commas"""
        # If it parsed successfully, no trailing commas exist
        # This is a parsing validation test
        assert vscode_settings is not None, "Valid JSON should not have trailing commas"


class TestSettingsValidation:
    """Test validity of settings values"""
    
    def test_all_keys_are_strings(self, vscode_settings):
        """
        Verify that every top-level key in the parsed VSCode settings object is a string.
        """
        for key in vscode_settings.keys():
            assert isinstance(key, str), f"Setting key should be string: {key}"
    
    def test_setting_keys_follow_convention(self, vscode_settings):
        """
        Ensure top-level VSCode setting keys follow expected naming conventions.
        
        Checks that each top-level key either contains a dot (sectioned setting) or begins with a lowercase letter; raises an assertion error naming any offending key.
        
        Parameters:
            vscode_settings (dict): Parsed .vscode/settings.json as a mapping of keys to values.
        """
        # VSCode settings typically use camelCase with dots
        for key in vscode_settings.keys():
            assert '.' in key or key[0].islower(), \
                f"Setting key '{key}' should follow VSCode naming convention"
    
    def test_array_values_contain_strings(self, vscode_settings):
        """
        Validate that any setting whose value is a list contains only allowed JSON value types.
        
        Allowed item types are `str`, `int`, `bool`, and `dict`; the test fails if any list contains an item of a different type.
        """
        for key, value in vscode_settings.items():
            if isinstance(value, list):
                for item in value:
                    assert isinstance(item, (str, int, bool, dict)), \
                        f"Array items in '{key}' should be valid JSON types"


class TestBranchNameValidation:
    """Test branch name configurations"""
    
    def test_ignored_branch_names_are_valid(self, vscode_settings):
        """Test that branch names are valid strings"""
        ignored = vscode_settings.get('githubPullRequests.ignoredPullRequestBranches', [])
        for branch in ignored:
            assert isinstance(branch, str), f"Branch name should be string: {branch}"
            assert len(branch) > 0, "Branch name should not be empty"
    
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


class TestDirectoryStructure:
    """Test .vscode directory structure"""
    
    def test_vscode_directory_exists(self):
        """Test that .vscode directory exists"""
        vscode_dir = Path('.vscode')
        assert vscode_dir.exists(), ".vscode directory should exist"
        assert vscode_dir.is_dir(), ".vscode should be a directory"
    
    def test_settings_in_correct_location(self, vscode_settings_path):
        """
        Verify settings.json path is located inside the .vscode directory.
        """
        assert '.vscode' in str(vscode_settings_path), \
            "settings.json should be in .vscode directory"


class TestWorkspaceBestPractices:
    """Test workspace configuration best practices"""
    
    def test_settings_file_size_reasonable(self, vscode_raw):
        """
        Ensure the VSCode workspace settings file is under 10,000 characters.
        
        Fail the test if the raw settings content length is 10,000 characters or greater to prevent excessively large workspace settings files.
        """
        # Should be reasonable size for workspace settings
        assert len(vscode_raw) < 10000, \
            "Settings file seems excessively large (>10KB)"
    
    def test_no_sensitive_information(self, vscode_raw):
        """
        Ensure the raw settings content contains no sensitive values for common secret keywords.
        
        Checks for occurrences of 'password', 'token', 'api_key', 'secret', and 'credential' (case-insensitive).
        If any of these appear in the file, they must appear only as setting keys (the left side of a colon); an assertion is raised if any occurrence appears in a value.
        
        Parameters:
            vscode_raw (str): Raw string content of the .vscode/settings.json file.
        
        Raises:
            AssertionError: If a sensitive keyword is found where it appears to be a value rather than a key.
        """
        sensitive_patterns = ['password', 'token', 'api_key', 'secret', 'credential']
        lower_content = vscode_raw.lower()
        
        for pattern in sensitive_patterns:
            if pattern in lower_content:
                # Check if it's just a setting name (key), not a value
                lines = [l for l in vscode_raw.split('\n') if pattern in l.lower()]
                for line in lines:
                    # Should only be on left side of colon (key name)
                    if ':' in line:
                        key_part = line.split(':')[0]
                        assert pattern in key_part.lower(), \
                            f"Potential sensitive data '{pattern}' found in settings"
    
    def test_no_absolute_paths(self, vscode_raw):
        """Test that settings don't use user-specific absolute paths"""
        # Check for common absolute path patterns
        suspicious_paths = ['/Users/', '/home/', 'C:\\Users\\', '/Documents/']
        
        for path_pattern in suspicious_paths:
            assert path_pattern not in vscode_raw, \
                f"Settings should not contain user-specific path '{path_pattern}'"


class TestEdgeCases:
    """Test edge cases and potential issues"""
    
    def test_file_not_empty(self, vscode_raw):
        """Test that settings file is not empty"""
        assert len(vscode_raw.strip()) > 0, "Settings file should not be empty"
    
    def test_settings_object_not_empty(self, vscode_settings):
        """Test that settings object has content"""
        assert len(vscode_settings.keys()) > 0, "Should have at least one setting"
    
    def test_no_duplicate_keys(self, vscode_raw):
        """
        Assert the settings.json contains at most one occurrence of the `githubPullRequests.ignoredPullRequestBranches` top-level key.
        
        Checks the raw file content and raises an AssertionError if the exact key appears more than once.
        """
        # Python's json.load() will use last value for duplicates
        # Check that parsing matches raw count
        key_count = vscode_raw.count('"githubPullRequests.ignoredPullRequestBranches"')
        assert key_count <= 1, "Should not have duplicate keys"
    
    def test_properly_closed_braces(self, vscode_raw):
        """Test that JSON has properly matched braces"""
        open_braces = vscode_raw.count('{')
        close_braces = vscode_raw.count('}')
        assert open_braces == close_braces, "Braces should be properly matched"
        
        open_brackets = vscode_raw.count('[')
        close_brackets = vscode_raw.count(']')
        assert open_brackets == close_brackets, "Brackets should be properly matched"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])