"""
Tests for pytest configuration validation.

This module validates that pytest is properly configured for the project:
- pytest.ini settings are correct
- Test discovery patterns are appropriate
- Markers are properly defined
- Coverage settings are reasonable
- Output formatting is configured
"""

import pytest
import configparser
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """
    Return the repository root directory as a Path.
    
    Returns:
        pathlib.Path: Path to the repository root (parent of this file's parent).
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def pytest_ini_path(repo_root):
    """
    Return the path to the repository's pytest.ini file.
    
    Parameters:
    	repo_root (pathlib.Path): Repository root directory.
    
    Returns:
    	path (pathlib.Path): Path to `pytest.ini` at the repository root.
    """
    return repo_root / 'pytest.ini'


@pytest.fixture(scope='module')
def pytest_config(pytest_ini_path):
    """
    Load and parse the pytest.ini file at the given path.
    
    Parameters:
        pytest_ini_path (str | os.PathLike): Path to the pytest.ini file to read.
    
    Returns:
        config (configparser.ConfigParser): Parser populated with the contents of the pytest.ini.
    """
    config = configparser.ConfigParser()
    config.read(pytest_ini_path)
    return config


class TestPytestIniExists:
    """Test that pytest.ini exists and is readable"""
    
    def test_pytest_ini_exists(self, pytest_ini_path):
        """Test that pytest.ini file exists"""
        assert pytest_ini_path.exists(), \
            "pytest.ini must exist at repository root"
    
    def test_pytest_ini_is_readable(self, pytest_ini_path):
        """
        Assert that the repository's pytest.ini can be opened and contains at least one character.
        
        Parameters:
            pytest_ini_path (pathlike): Path to the pytest.ini file provided by the fixture.
        """
        with open(pytest_ini_path, 'r') as f:
            content = f.read()
            assert len(content) > 0, "pytest.ini should not be empty"


class TestPytestConfiguration:
    """Test pytest configuration settings"""
    
    def test_pytest_section_exists(self, pytest_config):
        """
        Assert that the repository's pytest.ini contains a [pytest] section.
        
        Parameters:
            pytest_config (configparser.ConfigParser): Parsed contents of pytest.ini used to inspect configured sections.
        """
        assert 'pytest' in pytest_config.sections(), \
            "pytest.ini should have [pytest] section"
    
    def test_testpaths_configured(self, pytest_config):
        """
        Verify that pytest.ini configures testpaths.
        
        If a [pytest] section is present in the parsed pytest.ini, assert that it contains a 'testpaths' setting; otherwise the test is a no-op.
        """
        if 'pytest' in pytest_config.sections():
            assert 'testpaths' in pytest_config['pytest'], \
                "pytest.ini should configure testpaths"
    
    def test_testpaths_points_to_tests(self, pytest_config):
        """Test that testpaths points to tests directory"""
        if 'pytest' in pytest_config.sections() and \
           'testpaths' in pytest_config['pytest']:
            testpaths = pytest_config['pytest']['testpaths']
            assert 'tests' in testpaths, \
                "testpaths should include 'tests' directory"
    
    def test_python_files_pattern_configured(self, pytest_config):
        """Test that python_files pattern is configured"""
        if 'pytest' in pytest_config.sections():
            assert 'python_files' in pytest_config['pytest'], \
                "pytest.ini should configure python_files pattern"
    
    def test_python_files_uses_test_prefix(self, pytest_config):
        """Test that python_files pattern uses test_ prefix"""
        if 'pytest' in pytest_config.sections() and \
           'python_files' in pytest_config['pytest']:
            pattern = pytest_config['pytest']['python_files']
            assert 'test_' in pattern, \
                "python_files should match test_*.py pattern"
    
    def test_python_classes_configured(self, pytest_config):
        """
        Ensure pytest.ini configures a python_classes test discovery pattern.
        
        If a `[pytest]` section exists, asserts that it contains a `python_classes` entry.
        
        Parameters:
            pytest_config (configparser.ConfigParser): Parsed pytest.ini configuration.
        """
        if 'pytest' in pytest_config.sections():
            assert 'python_classes' in pytest_config['pytest'], \
                "pytest.ini should configure python_classes pattern"
    
    def test_python_classes_uses_test_prefix(self, pytest_config):
        """
        Assert that the pytest `python_classes` pattern includes the `Test` prefix.
        
        Checks the parsed pytest.ini and, when a `[pytest]` section with `python_classes` is present, fails the test unless the configured pattern contains `Test`.
        
        Parameters:
            pytest_config (configparser.ConfigParser): Parsed configuration for pytest.ini.
        """
        if 'pytest' in pytest_config.sections() and \
           'python_classes' in pytest_config['pytest']:
            pattern = pytest_config['pytest']['python_classes']
            assert 'Test' in pattern, \
                "python_classes should match Test* pattern"
    
    def test_python_functions_configured(self, pytest_config):
        """
        Verify the pytest.ini configures the `python_functions` test discovery pattern.
        
        If a `[pytest]` section is present in the parsed config, assert that it contains a `python_functions` entry.
        """
        if 'pytest' in pytest_config.sections():
            assert 'python_functions' in pytest_config['pytest'], \
                "pytest.ini should configure python_functions pattern"
    
    def test_python_functions_uses_test_prefix(self, pytest_config):
        """
        Check that the pytest `python_functions` pattern includes the `test_` prefix.
        
        Parameters:
            pytest_config (configparser.ConfigParser): Parsed pytest.ini contents; if the `[pytest]` section or `python_functions` option is absent, the test does not perform an assertion.
        """
        if 'pytest' in pytest_config.sections() and \
           'python_functions' in pytest_config['pytest']:
            pattern = pytest_config['pytest']['python_functions']
            assert 'test_' in pattern, \
                "python_functions should match test_* pattern"


class TestPytestAddopts:
    """Test pytest addopts (additional options)"""
    
    def test_addopts_configured(self, pytest_config):
        """
        Skip the test when a [pytest] section exists but the `addopts` option is not set in pytest.ini.
        
        If the parsed pytest configuration contains a `[pytest]` section and that section lacks an `addopts` entry, the test is skipped with a note that `addopts` is optional. If the `[pytest]` section is absent, the function does nothing.
        
        Parameters:
            pytest_config (configparser.ConfigParser): Parsed contents of the repository's pytest.ini.
        """
        if 'pytest' in pytest_config.sections():
            # addopts is recommended but optional
            has_addopts = 'addopts' in pytest_config['pytest']
            if not has_addopts:
                pytest.skip("addopts is optional")
    
    def test_verbose_output_enabled(self, pytest_config):
        """
        Check that pytest `addopts` includes `-v` or `--verbose` when an `[pytest]` section defines `addopts`.
        
        Parameters:
            pytest_config (configparser.ConfigParser): Parsed pytest.ini configuration.
        """
        if 'pytest' in pytest_config.sections() and \
           'addopts' in pytest_config['pytest']:
            addopts = pytest_config['pytest']['addopts']
            assert '-v' in addopts or '--verbose' in addopts, \
                "addopts should enable verbose output (-v)"
    
    def test_traceback_configured(self, pytest_config):
        """
        Check that when the [pytest] section contains an `addopts` option, its value specifies a `--tb` (traceback) format of `short`, `line` or `native` for readable tracebacks.
        
        Parameters:
            pytest_config (configparser.ConfigParser): Parsed pytest.ini configuration.
        """
        if 'pytest' in pytest_config.sections() and \
           'addopts' in pytest_config['pytest']:
            addopts = pytest_config['pytest']['addopts']
            has_tb = '--tb' in addopts
            if has_tb:
                # Should use short or line format for clarity
                assert '--tb=short' in addopts or '--tb=line' in addopts or \
                       '--tb=native' in addopts, \
                    "traceback should be configured for readability"


class TestTestDiscovery:
    """Test that test discovery works correctly"""
    
    def test_test_files_are_discoverable(self, repo_root):
        """
        Check that at least one test file following the tests/**/test_*.py pattern exists under the repository's tests/ directory.
        
        Asserts that at least one file matches the recursive glob pattern tests/**/test_*.py.
        """
        test_dir = repo_root / 'tests'
        test_files = list(test_dir.rglob('test_*.py'))
        
        assert len(test_files) > 0, \
            "Should discover test files with test_* pattern"
    
    def test_no_test_files_outside_tests_dir(self, repo_root):
        """
        Assert no top-level files match the `test_*.py` pattern so test files are only under the `tests/` directory.
        
        Parameters:
            repo_root (pathlib.Path): Repository root to search for top-level test files.
        """
        # Search for test files in root and other directories
        test_files_in_root = list(repo_root.glob('test_*.py'))
        
        assert len(test_files_in_root) == 0, \
            "Test files should only be in tests/ directory"
    
    def test_init_files_present_for_discovery(self, repo_root):
        """
        Ensure package marker files exist in tests/ and tests/workflows/ so pytest can discover tests.
        
        This verifies the presence of tests/__init__.py and tests/workflows/__init__.py.
        """
        tests_dir = repo_root / 'tests'
        workflows_dir = tests_dir / 'workflows'
        
        assert (tests_dir / '__init__.py').exists(), \
            "tests/__init__.py should exist"
        assert (workflows_dir / '__init__.py').exists(), \
            "tests/workflows/__init__.py should exist"


class TestRequirementsTxt:
    """Test that requirements.txt is properly configured"""
    
    def test_requirements_file_exists(self, repo_root):
        """Test that tests/requirements.txt exists"""
        requirements = repo_root / 'tests' / 'requirements.txt'
        assert requirements.exists(), \
            "tests/requirements.txt should exist"
    
    def test_requirements_includes_pytest(self, repo_root):
        """
        Verify that tests/requirements.txt mentions pytest and includes a version specifier.
        
        Asserts the file contains 'pytest' (case-insensitive) and a version operator ('>=' or '==').
        """
        requirements = repo_root / 'tests' / 'requirements.txt'
        with open(requirements, 'r') as f:
            content = f.read()
            assert 'pytest' in content.lower(), \
                "requirements.txt should include pytest"
            # Should have version specifier
            assert '>=' in content or '==' in content, \
                "requirements.txt should specify pytest version"
    
    def test_requirements_includes_pyyaml(self, repo_root):
        """
        Verify tests/requirements.txt declares PyYAML as a dependency.
        
        Searches the tests/requirements.txt file for the substring "yaml" in a case-insensitive manner.
        
        Parameters:
            repo_root (pathlib.Path): Path to the repository root.
        """
        requirements = repo_root / 'tests' / 'requirements.txt'
        with open(requirements, 'r') as f:
            content = f.read()
            assert 'yaml' in content.lower(), \
                "requirements.txt should include PyYAML"
    
    def test_requirements_has_reasonable_versions(self, repo_root):
        """Test that requirements specify reasonable minimum versions"""
        requirements = repo_root / 'tests' / 'requirements.txt'
        with open(requirements, 'r') as f:
            lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Should have version specifier
                    assert '>=' in line or '==' in line or '~=' in line, \
                        f"Dependency should have version: {line}"


class TestProjectStructure:
    """Test overall project test structure"""
    
    def test_tests_directory_exists(self, repo_root):
        """
        Assert that the repository contains a top-level `tests/` directory.
        """
        tests_dir = repo_root / 'tests'
        assert tests_dir.exists(), "tests/ directory should exist"
        assert tests_dir.is_dir(), "tests/ should be a directory"
    
    def test_workflows_subdirectory_exists(self, repo_root):
        """Test that tests/workflows/ subdirectory exists"""
        workflows_dir = repo_root / 'tests' / 'workflows'
        assert workflows_dir.exists(), \
            "tests/workflows/ directory should exist"
    
    def test_no_pycache_in_repo(self, repo_root):
        """
        Check that the repository's .gitignore excludes Python bytecode artifacts.
        
        Reads the top-level .gitignore (if present) and asserts it contains '__pycache__' or '*.pyc'.
        """
        # Check if .gitignore exists and includes __pycache__
        gitignore = repo_root / '.gitignore'
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
                assert '__pycache__' in content or '*.pyc' in content, \
                    ".gitignore should ignore __pycache__ and .pyc files"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])