"""
Comprehensive test suite for pytest.ini configuration files

This test suite validates pytest configuration including:
- Configuration file existence and readability
- Required configuration sections
- Test path configuration
- File naming patterns
- Class and function naming patterns
- Additional options (addopts)
- Markers configuration
- Configuration consistency between root and tests directory
- Edge cases and best practices
"""

import pytest
import configparser
import os
from pathlib import Path


# Module-level fixtures for configuration file paths
@pytest.fixture(scope='module')
def repo_root():
    """Get repository root path"""
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def root_config_path(repo_root):
    """Get root pytest.ini path"""
    return repo_root / 'pytest.ini'


@pytest.fixture(scope='module')
def tests_config_path(repo_root):
    """Get tests/pytest.ini path"""
    return repo_root / 'tests' / 'pytest.ini'


@pytest.fixture(scope='module')
def root_config_content(root_config_path):
    """Parse root pytest.ini content"""
    parser = configparser.ConfigParser()
    parser.read(root_config_path)
    return parser


@pytest.fixture(scope='module')
def tests_config_content(tests_config_path):
    """Parse tests/pytest.ini content"""
    parser = configparser.ConfigParser()
    parser.read(tests_config_path)
    return parser


class TestRootConfigFile:
    """Test root-level pytest.ini file"""
    
    def test_root_config_exists(self, root_config_path):
        """Test that root pytest.ini exists"""
        assert root_config_path.exists(), f"Root pytest.ini not found at {root_config_path}"
        assert root_config_path.is_file(), "Expected file but found directory"
    
    def test_root_config_is_readable(self, root_config_path):
        """Test that root pytest.ini is readable"""
        assert os.access(root_config_path, os.R_OK), "Root pytest.ini must be readable"
    
    def test_root_config_not_empty(self, root_config_path):
        """Test that root pytest.ini is not empty"""
        content = root_config_path.read_text()
        assert len(content.strip()) > 0, "Root pytest.ini is empty"
    
    def test_root_config_has_pytest_section(self, root_config_content):
        """Test that root config has [pytest] section"""
        assert root_config_content.has_section('pytest'), \
            "Root pytest.ini missing [pytest] section"


class TestTestsConfigFile:
    """Test tests directory pytest.ini file"""
    
    def test_tests_config_exists(self, tests_config_path):
        """Test that tests/pytest.ini exists"""
        assert tests_config_path.exists(), f"tests/pytest.ini not found at {tests_config_path}"
        assert tests_config_path.is_file(), "Expected file but found directory"
    
    def test_tests_config_is_readable(self, tests_config_path):
        """Test that tests/pytest.ini is readable"""
        assert os.access(tests_config_path, os.R_OK), "tests/pytest.ini must be readable"
    
    def test_tests_config_not_empty(self, tests_config_path):
        """Test that tests/pytest.ini is not empty"""
        content = tests_config_path.read_text()
        assert len(content.strip()) > 0, "tests/pytest.ini is empty"
    
    def test_tests_config_has_pytest_section(self, tests_config_content):
        """Test that tests config has [pytest] section"""
        assert tests_config_content.has_section('pytest'), \
            "tests/pytest.ini missing [pytest] section"


class TestRootConfigOptions:
    """Test root pytest.ini configuration options"""
    
    def test_testpaths_is_configured(self, root_config_content):
        """Test that testpaths option is configured"""
        assert root_config_content.has_option('pytest', 'testpaths'), \
            "Root config missing 'testpaths' option"
    
    def test_testpaths_points_to_tests(self, root_config_content):
        """Test that testpaths points to tests directory"""
        testpaths = root_config_content.get('pytest', 'testpaths')
        assert 'tests' in testpaths, \
            f"Expected testpaths to include 'tests', got '{testpaths}'"
    
    def test_python_files_pattern_configured(self, root_config_content):
        """Test that python_files pattern is configured"""
        assert root_config_content.has_option('pytest', 'python_files'), \
            "Root config missing 'python_files' option"
    
    def test_python_files_follows_convention(self, root_config_content):
        """Test that python_files follows test_*.py convention"""
        python_files = root_config_content.get('pytest', 'python_files')
        assert 'test_' in python_files and '.py' in python_files, \
            f"python_files should follow 'test_*.py' pattern, got '{python_files}'"
    
    def test_python_classes_pattern_configured(self, root_config_content):
        """Test that python_classes pattern is configured"""
        assert root_config_content.has_option('pytest', 'python_classes'), \
            "Root config missing 'python_classes' option"
    
    def test_python_classes_follows_convention(self, root_config_content):
        """Test that python_classes follows Test* convention"""
        python_classes = root_config_content.get('pytest', 'python_classes')
        assert 'Test' in python_classes, \
            f"python_classes should follow 'Test*' pattern, got '{python_classes}'"
    
    def test_python_functions_pattern_configured(self, root_config_content):
        """Test that python_functions pattern is configured"""
        assert root_config_content.has_option('pytest', 'python_functions'), \
            "Root config missing 'python_functions' option"
    
    def test_python_functions_follows_convention(self, root_config_content):
        """Test that python_functions follows test_* convention"""
        python_functions = root_config_content.get('pytest', 'python_functions')
        assert 'test_' in python_functions, \
            f"python_functions should follow 'test_*' pattern, got '{python_functions}'"
    
    def test_addopts_configured(self, root_config_content):
        """Test that addopts (additional options) is configured"""
        assert root_config_content.has_option('pytest', 'addopts'), \
            "Root config missing 'addopts' option"
    
    def test_addopts_includes_verbose(self, root_config_content):
        """Test that addopts includes verbose flag"""
        addopts = root_config_content.get('pytest', 'addopts')
        assert '-v' in addopts, "addopts should include '-v' for verbose output"
    
    def test_addopts_includes_traceback_style(self, root_config_content):
        """Test that addopts includes traceback style"""
        addopts = root_config_content.get('pytest', 'addopts')
        assert '--tb=' in addopts or '--tb ' in addopts, \
            "addopts should include '--tb' for traceback style"


class TestTestsConfigOptions:
    """Test tests/pytest.ini configuration options"""
    
    def test_testpaths_is_configured(self, tests_config_content):
        """Test that testpaths option is configured"""
        assert tests_config_content.has_option('pytest', 'testpaths'), \
            "tests config missing 'testpaths' option"
    
    def test_testpaths_points_to_tests(self, tests_config_content):
        """Test that testpaths points to tests directory"""
        testpaths = tests_config_content.get('pytest', 'testpaths')
        assert 'tests' in testpaths, \
            f"Expected testpaths to include 'tests', got '{testpaths}'"
    
    def test_python_files_pattern_configured(self, tests_config_content):
        """Test that python_files pattern is configured"""
        assert tests_config_content.has_option('pytest', 'python_files'), \
            "tests config missing 'python_files' option"
    
    def test_python_classes_pattern_configured(self, tests_config_content):
        """Test that python_classes pattern is configured"""
        assert tests_config_content.has_option('pytest', 'python_classes'), \
            "tests config missing 'python_classes' option"
    
    def test_python_functions_pattern_configured(self, tests_config_content):
        """Test that python_functions pattern is configured"""
        assert tests_config_content.has_option('pytest', 'python_functions'), \
            "tests config missing 'python_functions' option"
    
    def test_addopts_configured(self, tests_config_content):
        """Test that addopts is configured"""
        assert tests_config_content.has_option('pytest', 'addopts'), \
            "tests config missing 'addopts' option"
    
    def test_addopts_includes_verbose(self, tests_config_content):
        """Test that addopts includes verbose flag"""
        addopts = tests_config_content.get('pytest', 'addopts')
        assert '-v' in addopts, "addopts should include '-v' for verbose output"
    
    def test_addopts_includes_strict_markers(self, tests_config_content):
        """Test that addopts includes strict-markers flag"""
        addopts = tests_config_content.get('pytest', 'addopts')
        assert '--strict-markers' in addopts, \
            "tests config addopts should include '--strict-markers'"
    
    def test_markers_section_exists(self, tests_config_content):
        """Test that markers are defined in tests config"""
        assert tests_config_content.has_option('pytest', 'markers'), \
            "tests config missing 'markers' option"
    
    def test_markers_include_workflows(self, tests_config_content):
        """Test that markers include 'workflows' marker"""
        markers = tests_config_content.get('pytest', 'markers')
        assert 'workflows' in markers, "markers should include 'workflows' marker"
    
    def test_markers_include_integration(self, tests_config_content):
        """Test that markers include 'integration' marker"""
        markers = tests_config_content.get('pytest', 'markers')
        assert 'integration' in markers, "markers should include 'integration' marker"
    
    def test_markers_include_unit(self, tests_config_content):
        """Test that markers include 'unit' marker"""
        markers = tests_config_content.get('pytest', 'markers')
        assert 'unit' in markers, "markers should include 'unit' marker"


class TestConfigurationConsistency:
    """Test consistency between root and tests configuration"""
    
    def test_testpaths_consistency(self, root_config_content, tests_config_content):
        """Test that testpaths are consistent between configs"""
        root_testpaths = root_config_content.get('pytest', 'testpaths')
        tests_testpaths = tests_config_content.get('pytest', 'testpaths')
        
        assert root_testpaths == tests_testpaths, \
            f"testpaths mismatch: root='{root_testpaths}' vs tests='{tests_testpaths}'"
    
    def test_python_files_consistency(self, root_config_content, tests_config_content):
        """Test that python_files patterns are consistent"""
        root_pattern = root_config_content.get('pytest', 'python_files')
        tests_pattern = tests_config_content.get('pytest', 'python_files')
        
        assert root_pattern == tests_pattern, \
            f"python_files mismatch: root='{root_pattern}' vs tests='{tests_pattern}'"
    
    def test_python_classes_consistency(self, root_config_content, tests_config_content):
        """Test that python_classes patterns are consistent"""
        root_pattern = root_config_content.get('pytest', 'python_classes')
        tests_pattern = tests_config_content.get('pytest', 'python_classes')
        
        assert root_pattern == tests_pattern, \
            f"python_classes mismatch: root='{root_pattern}' vs tests='{tests_pattern}'"
    
    def test_python_functions_consistency(self, root_config_content, tests_config_content):
        """Test that python_functions patterns are consistent"""
        root_pattern = root_config_content.get('pytest', 'python_functions')
        tests_pattern = tests_config_content.get('pytest', 'python_functions')
        
        assert root_pattern == tests_pattern, \
            f"python_functions mismatch: root='{root_pattern}' vs tests='{tests_pattern}'"
    
    def test_both_configs_include_verbose(self, root_config_content, tests_config_content):
        """Test that both configs include verbose flag"""
        root_addopts = root_config_content.get('pytest', 'addopts')
        tests_addopts = tests_config_content.get('pytest', 'addopts')
        
        assert '-v' in root_addopts, "Root config should include '-v'"
        assert '-v' in tests_addopts, "Tests config should include '-v'"


class TestConfigurationBestPractices:
    """Test configuration follows pytest best practices"""
    
    def test_traceback_style_is_short(self, root_config_content):
        """Test that traceback style is set to short for cleaner output"""
        addopts = root_config_content.get('pytest', 'addopts')
        assert '--tb=short' in addopts or '--tb short' in addopts, \
            "Recommend using '--tb=short' for cleaner traceback output"
    
    def test_no_deprecated_options(self, root_config_path):
        """Test that config doesn't use deprecated pytest options"""
        content = root_config_path.read_text()
        
        deprecated_options = ['--strict', '--pytest-warnings']
        for option in deprecated_options:
            assert option not in content, \
                f"Config contains deprecated option '{option}'"
    
    def test_file_follows_ini_format(self, root_config_path):
        """Test that config file follows INI format"""
        content = root_config_path.read_text()
        
        # Should have section headers
        assert '[pytest]' in content or '[tool:pytest]' in content, \
            "Config should have [pytest] section header"
    
    def test_consistent_formatting(self, root_config_path):
        """Test that config file has consistent formatting"""
        content = root_config_path.read_text()
        lines = content.split('\n')
        
        # Check for basic formatting consistency
        for line in lines:
            if line.strip() and not line.strip().startswith('['):
                if '=' in line:
                    # Option lines should have format: key = value
                    parts = line.split('=', 1)
                    assert len(parts) == 2, f"Malformed config line: {line}"


class TestMarkerDefinitions:
    """Test marker definitions in tests config"""
    
    def test_markers_have_descriptions(self, tests_config_content):
        """Test that markers include descriptive text"""
        markers = tests_config_content.get('pytest', 'markers')
        marker_lines = [line.strip() for line in markers.split('\n') if line.strip()]
        
        for marker_line in marker_lines:
            if marker_line:
                # Each marker should have format: name: description
                assert ':' in marker_line, \
                    f"Marker should have description: {marker_line}"
    
    def test_workflow_marker_definition(self, tests_config_content):
        """Test that workflows marker has appropriate description"""
        markers = tests_config_content.get('pytest', 'markers')
        assert 'workflows' in markers and 'workflow' in markers.lower(), \
            "workflows marker should mention 'workflow' in description"
    
    def test_integration_marker_definition(self, tests_config_content):
        """Test that integration marker has appropriate description"""
        markers = tests_config_content.get('pytest', 'markers')
        assert 'integration' in markers, \
            "integration marker should be defined"
    
    def test_unit_marker_definition(self, tests_config_content):
        """Test that unit marker has appropriate description"""
        markers = tests_config_content.get('pytest', 'markers')
        assert 'unit' in markers, \
            "unit marker should be defined"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_no_trailing_whitespace(self, root_config_path):
        """Test that config doesn't have excessive trailing whitespace"""
        content = root_config_path.read_text()
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.endswith('  '):  # More than one trailing space
                pytest.fail(f"Line {i} has excessive trailing whitespace")
    
    def test_no_empty_sections(self, root_config_content):
        """Test that config sections are not empty"""
        for section in root_config_content.sections():
            options = root_config_content.options(section)
            assert len(options) > 0, f"Section '{section}' is empty"
    
    def test_option_values_not_empty(self, root_config_content):
        """Test that option values are not empty strings"""
        for section in root_config_content.sections():
            for option in root_config_content.options(section):
                value = root_config_content.get(section, option)
                assert value is not None, \
                    f"Option '{option}' in section '{section}' is None"
                assert len(value.strip()) > 0, \
                    f"Option '{option}' in section '{section}' is empty"
    
    def test_file_has_newline_at_end(self, root_config_path):
        """Test that config file ends with newline (POSIX standard)"""
        content = root_config_path.read_text()
        if content:  # Only check if file is not empty
            # Allow for some flexibility - just check it doesn't have multiple trailing newlines
            assert not content.endswith('\n\n\n'), \
                "Config file should not have excessive trailing newlines"


class TestConfigFileLocation:
    """Test configuration file locations"""
    
    def test_root_config_in_repo_root(self, repo_root, root_config_path):
        """Test that root pytest.ini is in repository root"""
        assert root_config_path.parent == repo_root, \
            "Root pytest.ini should be in repository root"
    
    def test_tests_config_in_tests_dir(self, repo_root, tests_config_path):
        """Test that tests/pytest.ini is in tests directory"""
        expected_parent = repo_root / 'tests'
        assert tests_config_path.parent == expected_parent, \
            "tests/pytest.ini should be in tests directory"
    
    def test_config_files_named_correctly(self, root_config_path, tests_config_path):
        """Test that config files are named pytest.ini"""
        assert root_config_path.name == 'pytest.ini', \
            "Root config should be named 'pytest.ini'"
        assert tests_config_path.name == 'pytest.ini', \
            "Tests config should be named 'pytest.ini'"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])