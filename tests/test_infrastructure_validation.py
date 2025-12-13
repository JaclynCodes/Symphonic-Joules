"""
Infrastructure validation tests for the test suite.

This module validates that the test infrastructure is properly configured:
- pytest.ini settings are correct
- Test dependencies are specified
- Test discovery works correctly
- Test files follow naming conventions
- Module structure is correct
"""

import pytest
import configparser
import subprocess
import sys
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def tests_dir(repo_root):
    """Get the tests directory."""
    return repo_root / 'tests'


@pytest.fixture(scope='module')
def pytest_ini_path(repo_root):
    """Get pytest.ini file path."""
    return repo_root / 'pytest.ini'


@pytest.fixture(scope='module')
def pytest_config(pytest_ini_path):
    """Load pytest.ini configuration."""
    config = configparser.ConfigParser()
    config.read(pytest_ini_path)
    return config


class TestPytestConfiguration:
    """Test pytest.ini configuration"""
    
    def test_pytest_ini_exists(self, pytest_ini_path):
        """Test that pytest.ini exists at repository root"""
        assert pytest_ini_path.exists(), \
            "pytest.ini must exist at repository root"
    
    def test_pytest_ini_is_readable(self, pytest_ini_path):
        """Test that pytest.ini is readable"""
        with open(pytest_ini_path, 'r') as file:
            content = file.read()
            assert len(content) > 0, "pytest.ini should not be empty"
    
    def test_pytest_section_exists(self, pytest_config):
        """Test that [pytest] section exists"""
        assert 'pytest' in pytest_config.sections(), \
            "pytest.ini should have [pytest] section"
    
    def test_testpaths_configured(self, pytest_config):
        """Test that testpaths is configured to tests directory"""
        if 'pytest' in pytest_config.sections():
            testpaths = pytest_config['pytest'].get('testpaths', '')
            assert 'tests' in testpaths, \
                "testpaths should point to tests directory"
    
    def test_python_files_pattern(self, pytest_config):
        """Test that python_files pattern is correctly configured"""
        if 'pytest' in pytest_config.sections():
            pattern = pytest_config['pytest'].get('python_files', '')
            assert 'test_' in pattern, \
                "python_files should match test_*.py pattern"
    
    def test_python_classes_pattern(self, pytest_config):
        """Test that python_classes pattern is correctly configured"""
        if 'pytest' in pytest_config.sections():
            pattern = pytest_config['pytest'].get('python_classes', '')
            assert 'Test' in pattern, \
                "python_classes should match Test* pattern"
    
    def test_python_functions_pattern(self, pytest_config):
        """Test that python_functions pattern is correctly configured"""
        if 'pytest' in pytest_config.sections():
            pattern = pytest_config['pytest'].get('python_functions', '')
            assert 'test_' in pattern, \
                "python_functions should match test_* pattern"
    
    def test_verbose_output_configured(self, pytest_config):
        """Test that verbose output is enabled"""
        if 'pytest' in pytest_config.sections():
            addopts = pytest_config['pytest'].get('addopts', '')
            assert '-v' in addopts or '--verbose' in addopts, \
                "addopts should enable verbose output"
    
    def test_traceback_format_configured(self, pytest_config):
        """Test that traceback format is configured for readability"""
        if 'pytest' in pytest_config.sections():
            addopts = pytest_config['pytest'].get('addopts', '')
            assert '--tb=' in addopts, \
                "addopts should configure traceback format"


class TestRequirements:
    """Test test dependencies configuration"""
    
    def test_requirements_file_exists(self, tests_dir):
        """Test that tests/requirements.txt exists"""
        requirements_path = tests_dir / 'requirements.txt'
        assert requirements_path.exists(), \
            "tests/requirements.txt must exist"
    
    def test_requirements_includes_pytest(self, tests_dir):
        """Test that requirements.txt includes pytest"""
        requirements_path = tests_dir / 'requirements.txt'
        with open(requirements_path, 'r') as f:
            content = f.read()
            assert 'pytest' in content.lower(), \
                "requirements.txt must include pytest"
    
    def test_pytest_version_specified(self, tests_dir):
        """Test that pytest version is specified"""
        requirements_path = tests_dir / 'requirements.txt'
        with open(requirements_path, 'r') as f:
            content = f.read()
            # Should have version specifier
            pytest_lines = [line for line in content.split('\n') 
                          if 'pytest' in line.lower() and not line.strip().startswith('#')]
            assert len(pytest_lines) > 0, "pytest should be in requirements"
            assert any('>=' in line or '==' in line for line in pytest_lines), \
                "pytest version should be specified"
    
    def test_pyyaml_included(self, tests_dir):
        """Test that PyYAML is included in requirements"""
        requirements_path = tests_dir / 'requirements.txt'
        with open(requirements_path, 'r') as f:
            content = f.read()
            assert 'yaml' in content.lower(), \
                "requirements.txt must include PyYAML"
    
    def test_pyyaml_version_specified(self, tests_dir):
        """Test that PyYAML version is specified"""
        requirements_path = tests_dir / 'requirements.txt'
        with open(requirements_path, 'r') as f:
            content = f.read()
            yaml_lines = [line for line in content.split('\n') 
                         if 'yaml' in line.lower() and not line.strip().startswith('#')]
            assert len(yaml_lines) > 0, "PyYAML should be in requirements"
            assert any('>=' in line or '==' in line for line in yaml_lines), \
                "PyYAML version should be specified"


class TestTestDiscovery:
    """Test that test discovery works correctly"""
    
    def test_test_files_are_discoverable(self, tests_dir):
        """Test that test files follow discoverable naming pattern"""
        test_files = list(tests_dir.rglob('test_*.py'))
        assert len(test_files) > 0, \
            "Should discover test files with test_* pattern"
    
    def test_only_valid_test_files_in_tests_dir(self, tests_dir):
        """Test that all .py files in tests/ are either tests or __init__"""
        py_files = list(tests_dir.rglob('*.py'))
        for py_file in py_files:
            name = py_file.name
            assert name.startswith('test_') or name == '__init__.py', \
                f"Unexpected Python file in tests/: {py_file.relative_to(tests_dir)}"
    
    def test_init_files_present(self, tests_dir):
        """Test that __init__.py files are present for package structure"""
        assert (tests_dir / '__init__.py').exists(), \
            "tests/__init__.py must exist"
        
        workflows_dir = tests_dir / 'workflows'
        if workflows_dir.exists():
            assert (workflows_dir / '__init__.py').exists(), \
                "tests/workflows/__init__.py must exist"
    
    def test_pytest_can_collect_tests(self, repo_root):
        """Test that pytest can collect tests without errors"""
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '--collect-only', '-q'],
            capture_output=True,
            text=True,
            cwd=str(repo_root)
        )
        
        # Collection should succeed
        assert result.returncode in [0, 5], \
            f"Test collection failed:\n{result.stderr}"


class TestProjectStructure:
    """Test overall project test structure"""
    
    def test_tests_directory_exists(self, repo_root):
        """Test that tests/ directory exists"""
        tests_dir = repo_root / 'tests'
        assert tests_dir.exists(), "tests/ directory must exist"
        assert tests_dir.is_dir(), "tests/ must be a directory"
    
    def test_workflows_subdirectory_exists(self, repo_root):
        """Test that tests/workflows/ subdirectory exists"""
        workflows_dir = repo_root / 'tests' / 'workflows'
        assert workflows_dir.exists(), "tests/workflows/ must exist"
        assert workflows_dir.is_dir(), "tests/workflows/ must be a directory"
    
    def test_no_pycache_committed(self, repo_root):
        """Test that __pycache__ is properly gitignored"""
        gitignore = repo_root / '.gitignore'
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
                assert '__pycache__' in content or '*.pyc' in content, \
                    ".gitignore should ignore __pycache__ and .pyc files"
    
    def test_no_test_files_in_root(self, repo_root):
        """Test that test files are only in tests/ directory"""
        root_test_files = list(repo_root.glob('test_*.py'))
        assert len(root_test_files) == 0, \
            "Test files should only be in tests/ directory"


class TestTestFileStructure:
    """Test that test files follow proper structure"""
    
    def test_test_files_have_docstrings(self, tests_dir):
        """Test that test files have module docstrings"""
        import ast
        
        test_files = list(tests_dir.rglob('test_*.py'))
        for test_file in test_files:
            with open(test_file, 'r') as f:
                tree = ast.parse(f.read())
                docstring = ast.get_docstring(tree)
                assert docstring is not None, \
                    f"{test_file.name} should have module docstring"
    
    def test_test_classes_follow_naming(self, tests_dir):
        """Test that test classes follow Test* naming convention"""
        import ast
        
        test_files = list(tests_dir.rglob('test_*.py'))
        for test_file in test_files:
            with open(test_file, 'r') as f:
                tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # If it has test methods, it should start with Test
                        has_test_methods = any(
                            isinstance(item, ast.FunctionDef) and item.name.startswith('test_')
                            for item in node.body
                        )
                        if has_test_methods:
                            assert node.name.startswith('Test'), \
                                f"Test class {node.name} in {test_file.name} should start with 'Test'"
    
    def test_test_methods_have_test_prefix(self, tests_dir):
        """Test that test methods follow test_* naming convention"""
        import ast
        
        test_files = list(tests_dir.rglob('test_*.py'))
        for test_file in test_files:
            with open(test_file, 'r') as f:
                try:
                    tree = ast.parse(f.read())
                except:
                    continue
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if not isinstance(item, ast.FunctionDef):
                                continue
                            # Skip private methods and test methods
                            if item.name.startswith('_') or item.name.startswith('test_'):
                                continue
                            # Check if it's a fixture
                            is_fixture = any(
                                (isinstance(decorator, ast.Call) and hasattr(decorator.func, 'attr') and decorator.func.attr == 'fixture') or
                                (isinstance(decorator, ast.Attribute) and decorator.attr == 'fixture')
                                for decorator in item.decorator_list
                            )
                            if not is_fixture:
                                assert False,                                     f"Method {item.name} in {node.name} ({test_file.name}) should start with 'test_' or be a fixture"
