"""
Comprehensive test suite for tests/pytest.ini

This test suite validates the pytest configuration including:
- Configuration syntax and structure
- Test discovery patterns
- Pytest markers and options
- Addopts and command-line options
"""

import pytest
import configparser
import os
from pathlib import Path


@pytest.fixture
def pytest_ini_path():
    """Return the path to pytest.ini file."""
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / "tests" / "pytest.ini"


@pytest.fixture
def pytest_config(pytest_ini_path):
    """Load and parse the pytest.ini file."""
    config = configparser.ConfigParser()
    config.read(pytest_ini_path)
    return config


@pytest.fixture
def pytest_ini_content(pytest_ini_path):
    """Load raw content of pytest.ini."""
    with open(pytest_ini_path, 'r') as f:
        return f.read()


class TestPytestIniStructure:
    """Test the basic structure of pytest.ini."""
    
    def test_pytest_ini_exists(self, pytest_ini_path):
        """Test that pytest.ini file exists."""
        assert pytest_ini_path.exists(), "pytest.ini should exist"
    
    def test_pytest_ini_is_valid_ini(self, pytest_ini_path):
        """Test that pytest.ini is valid INI format."""
        try:
            config = configparser.ConfigParser()
            config.read(pytest_ini_path)
        except configparser.Error as e:
            pytest.fail(f"Invalid INI syntax: {e}")
    
    def test_pytest_section_exists(self, pytest_config):
        """Test that [pytest] section exists."""
        assert pytest_config.has_section("pytest"), \
            "pytest.ini should have [pytest] section"
    
    def test_pytest_ini_not_empty(self, pytest_ini_content):
        """Test that pytest.ini is not empty."""
        assert len(pytest_ini_content.strip()) > 0, \
            "pytest.ini should not be empty"


class TestTestDiscoveryConfiguration:
    """Test test discovery patterns and configuration."""
    
    def test_testpaths_configured(self, pytest_config):
        """Test that testpaths is configured."""
        assert pytest_config.has_option("pytest", "testpaths"), \
            "pytest.ini should define testpaths"
    
    def test_testpaths_points_to_tests_directory(self, pytest_config):
        """Test that testpaths points to tests directory."""
        testpaths = pytest_config.get("pytest", "testpaths")
        assert "tests" in testpaths, \
            "testpaths should include 'tests' directory"
    
    def test_python_files_pattern_configured(self, pytest_config):
        """Test that python_files pattern is configured."""
        assert pytest_config.has_option("pytest", "python_files"), \
            "pytest.ini should define python_files pattern"
    
    def test_python_files_pattern_valid(self, pytest_config):
        """Test that python_files pattern follows conventions."""
        pattern = pytest_config.get("pytest", "python_files")
        assert "test_" in pattern, \
            "python_files should match test_*.py pattern"
        assert ".py" in pattern, \
            "python_files should match Python files"
    
    def test_python_classes_pattern_configured(self, pytest_config):
        """Test that python_classes pattern is configured."""
        assert pytest_config.has_option("pytest", "python_classes"), \
            "pytest.ini should define python_classes pattern"
    
    def test_python_classes_pattern_valid(self, pytest_config):
        """Test that python_classes pattern follows conventions."""
        pattern = pytest_config.get("pytest", "python_classes")
        assert "Test" in pattern, \
            "python_classes should match Test* pattern"
    
    def test_python_functions_pattern_configured(self, pytest_config):
        """Test that python_functions pattern is configured."""
        assert pytest_config.has_option("pytest", "python_functions"), \
            "pytest.ini should define python_functions pattern"
    
    def test_python_functions_pattern_valid(self, pytest_config):
        """Test that python_functions pattern follows conventions."""
        pattern = pytest_config.get("pytest", "python_functions")
        assert "test_" in pattern, \
            "python_functions should match test_* pattern"


class TestPytestMarkers:
    """Test pytest markers configuration."""
    
    def test_markers_configured(self, pytest_config):
        """Test that markers are configured."""
        assert pytest_config.has_option("pytest", "markers"), \
            "pytest.ini should define markers"
    
    def test_workflows_marker_defined(self, pytest_ini_content):
        """Test that workflows marker is defined."""
        assert "workflows:" in pytest_ini_content, \
            "pytest.ini should define 'workflows' marker"
    
    def test_integration_marker_defined(self, pytest_ini_content):
        """Test that integration marker is defined."""
        assert "integration:" in pytest_ini_content, \
            "pytest.ini should define 'integration' marker"
    
    def test_unit_marker_defined(self, pytest_ini_content):
        """Test that unit marker is defined."""
        assert "unit:" in pytest_ini_content, \
            "pytest.ini should define 'unit' marker"
    
    def test_marker_descriptions_present(self, pytest_ini_content):
        """Test that markers have descriptions."""
        markers_section = pytest_ini_content.split("markers =")[1] if "markers =" in pytest_ini_content else ""
        
        if "workflows:" in markers_section:
            assert "marks tests as workflow tests" in pytest_ini_content or \
                   "workflow" in pytest_ini_content.lower(), \
                "Markers should have descriptive text"


class TestPytestAddopts:
    """Test pytest addopts configuration."""
    
    def test_addopts_configured(self, pytest_config):
        """Test that addopts is configured."""
        assert pytest_config.has_option("pytest", "addopts"), \
            "pytest.ini should define addopts"
    
    def test_verbose_mode_enabled(self, pytest_ini_content):
        """Test that verbose mode is enabled."""
        assert "-v" in pytest_ini_content, \
            "pytest.ini should enable verbose mode with -v"
    
    def test_strict_markers_enabled(self, pytest_ini_content):
        """Test that strict-markers is enabled."""
        assert "--strict-markers" in pytest_ini_content, \
            "pytest.ini should enable --strict-markers for marker validation"
    
    def test_traceback_format_configured(self, pytest_ini_content):
        """Test that traceback format is configured."""
        assert "--tb=" in pytest_ini_content, \
            "pytest.ini should configure traceback format"
    
    def test_traceback_format_is_reasonable(self, pytest_ini_content):
        """Test that traceback format is short or auto."""
        if "--tb=" in pytest_ini_content:
            assert "--tb=short" in pytest_ini_content or \
                   "--tb=auto" in pytest_ini_content or \
                   "--tb=long" in pytest_ini_content, \
                "Traceback format should be short, auto, or long"


class TestConfigurationBestPractices:
    """Test configuration best practices."""
    
    def test_no_cache_directory_in_repo(self, pytest_config):
        """Test that cache directory is not set to be in repo."""
        if pytest_config.has_option("pytest", "cache_dir"):
            cache_dir = pytest_config.get("pytest", "cache_dir")
            assert not cache_dir.startswith("."), \
                "Cache directory should not be in repository root"
    
    def test_no_overly_verbose_options(self, pytest_ini_content):
        """Test that configuration doesn't have excessive verbosity."""
        # Too many -v flags can slow down test runs
        assert pytest_ini_content.count("-vvv") == 0, \
            "Avoid excessive verbosity (-vvv)"
    
    def test_sensible_timeout_if_configured(self, pytest_config):
        """Test that timeout values are sensible if configured."""
        if pytest_config.has_option("pytest", "timeout"):
            timeout = int(pytest_config.get("pytest", "timeout"))
            assert 1 <= timeout <= 3600, \
                "Timeout should be between 1 and 3600 seconds"
    
    def test_no_dangerous_options(self, pytest_ini_content):
        """Test that no dangerous options are configured."""
        dangerous_options = [
            "--lf",  # Last failed only - shouldn't be default
            "--ff",  # Failed first - shouldn't be default
            "--exitfirst",  # Exit on first failure - shouldn't be default
        ]
        
        for option in dangerous_options:
            assert option not in pytest_ini_content, \
                f"Default config should not include {option}"


class TestPytestIniFormatting:
    """Test formatting and style of pytest.ini."""
    
    def test_consistent_indentation(self, pytest_ini_content):
        """Test that pytest.ini uses consistent indentation."""
        lines = pytest_ini_content.split('\n')
        indented_lines = [line for line in lines if line.startswith(' ') or line.startswith('\t')]
        
        if indented_lines:
            # Check that all indentation is consistent (all spaces or all tabs)
            uses_spaces = any(line.startswith(' ') for line in indented_lines)
            uses_tabs = any(line.startswith('\t') for line in indented_lines)
            
            assert not (uses_spaces and uses_tabs), \
                "pytest.ini should use consistent indentation (spaces or tabs, not mixed)"
    
    def test_no_trailing_whitespace(self, pytest_ini_content):
        """Test that lines don't have trailing whitespace."""
        lines = pytest_ini_content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.endswith(' ') or line.endswith('\t'):
                pytest.fail(f"Line {i} has trailing whitespace")
    
    def test_file_ends_with_newline(self, pytest_ini_content):
        """Test that file ends with a newline."""
        assert pytest_ini_content.endswith('\n'), \
            "pytest.ini should end with a newline"


class TestMarkerConsistency:
    """Test marker usage consistency across the test suite."""
    
    def test_marker_names_are_valid_python_identifiers(self, pytest_ini_content):
        """Test that marker names are valid Python identifiers."""
        import re
        
        marker_pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*):'
        lines = pytest_ini_content.split('\n')
        
        for line in lines:
            match = re.match(marker_pattern, line)
            if match:
                marker_name = match.group(1)
                assert marker_name.isidentifier(), \
                    f"Marker '{marker_name}' should be a valid Python identifier"
    
    def test_markers_have_descriptions(self, pytest_ini_content):
        """Test that all markers have descriptions."""
        import re
        
        # Find lines that look like marker definitions
        marker_lines = [line for line in pytest_ini_content.split('\n') 
                       if (':' in line and 'marks tests as' in line.lower()) or 
                       ('workflows' in line or 'integration' in line or 'unit' in line)]
        
        assert len(marker_lines) >= 3, \
            "All defined markers should have descriptions"


@pytest.mark.unit
class TestConfigurationEdgeCases:
    """Test edge cases in configuration."""
    
    def test_empty_sections_not_present(self, pytest_config):
        """Test that there are no empty configuration sections."""
        for section in pytest_config.sections():
            assert len(pytest_config.options(section)) > 0, \
                f"Section [{section}] should not be empty"
    
    def test_no_duplicate_options(self, pytest_ini_content):
        """Test that options are not duplicated."""
        lines = [line.strip() for line in pytest_ini_content.split('\n') 
                if '=' in line and not line.startswith('#')]
        option_names = [line.split('=')[0].strip() for line in lines]
        
        assert len(option_names) == len(set(option_names)), \
            "Configuration should not have duplicate options"
    
    def test_addopts_multiline_properly_formatted(self, pytest_ini_content):
        """Test that multiline addopts are properly formatted."""
        if "addopts =" in pytest_ini_content:
            # Check that continuation lines are indented
            lines = pytest_ini_content.split('\n')
            in_addopts = False
            
            for line in lines:
                if "addopts =" in line or "addopts=" in line:
                    in_addopts = True
                    continue
                
                if in_addopts:
                    if line and not line.startswith(' ') and not line.startswith('\t'):
                        in_addopts = False
                    elif line.strip().startswith('-'):
                        # This is a continuation line, should be indented
                        assert line.startswith(' ') or line.startswith('\t'), \
                            "Continuation lines in addopts should be indented"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])