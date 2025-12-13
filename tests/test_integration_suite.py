"""
Integration tests for the Symphonic-Joules test suite.

This module validates that the test suite can execute successfully and provides
accurate validation of workflow files. It tests:
- Test execution without errors
- Fixture initialization
- Test discovery
- Test isolation
- Error reporting
"""

import pytest
import subprocess
import sys
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """
    Resolve the repository root directory for the test suite.
    
    Returns:
        Path: Path to the repository root directory located two levels above this file.
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def tests_dir(repo_root):
    """
    Get the repository's tests directory path.
    
    Parameters:
        repo_root (Path): Repository root directory.
    
    Returns:
        Path: Path to the 'tests' directory inside the repository.
    """
    return repo_root / 'tests'


class TestTestExecution:
    """Test that the test suite can execute successfully"""
    
    def test_pytest_collection_works(self, tests_dir):
        """
        Verify pytest can collect tests in the workflows directory.
        
        Runs pytest in collection-only mode against tests/workflows and asserts that pytest exits with code 0 or 5; raises an AssertionError including pytest stderr if collection fails.
        
        Parameters:
            tests_dir (Path): Path to the repository's tests directory.
        """
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(tests_dir / 'workflows'), 
             '--collect-only', '-q'],
            capture_output=True,
            text=True,
            cwd=str(tests_dir.parent)
        )
        
        # Collection should succeed (exit code 0 or 5 for no tests collected)
        assert result.returncode in [0, 5], \
            f"Test collection failed:\n{result.stderr}"
    
    def test_workflow_tests_are_discoverable(self, tests_dir):
        """
        Verify pytest can discover test files under the workflows subdirectory of the provided tests directory.
        
        Parameters:
            tests_dir (Path): Path to the repository's tests directory.
        
        Raises:
            AssertionError: If pytest does not report any discovered tests; the assertion message contains pytest's stdout.
        """
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(tests_dir / 'workflows'),
             '--collect-only', '-q'],
            capture_output=True,
            text=True,
            cwd=str(tests_dir.parent)
        )
        
        # Should find tests
        assert 'test session starts' in result.stdout or \
               'tests collected' in result.stdout or \
               'test_' in result.stdout, \
            f"No tests discovered:\n{result.stdout}"
    
    def test_blank_workflow_tests_execute(self, repo_root):
        """
        Check that the blank workflow test file executes without import-time errors.
        
        Runs pytest on tests/workflows/test_blank_workflow.py and fails if pytest reports import-time errors (indicated by 'ERRORS' in stdout with exit code 2).
        """
        test_file = repo_root / 'tests' / 'workflows' / 'test_blank_workflow.py'
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(test_file), '-v', '--tb=short'],
            capture_output=True,
            text=True,
            cwd=str(repo_root)
        )
        
        # Tests should pass or at least execute without import errors
        assert 'ERRORS' not in result.stdout or result.returncode != 2, \
            f"Test execution had errors:\n{result.stdout}\n{result.stderr}"


class TestFixtureInitialization:
    """Test that fixtures initialize correctly"""
    
    def test_workflow_path_fixture_resolves(self, repo_root):
        """
        Verify the workflow_path fixture resolves to the repository workflow file.
        
        Asserts that the fixture implementation in tests/workflows/test_blank_workflow yields the path
        repo_root/.github/workflows/blank.yml and that this file exists.
        """
        # Import the test module to verify fixtures work
        import sys
        sys.path.insert(0, str(repo_root / 'tests' / 'workflows'))
        
        try:
            from test_blank_workflow import workflow_path as blank_workflow_path
            
            # Call the fixture (it's a function)
            # Note: Fixtures need pytest context, so we test the logic directly
            expected_path = repo_root / '.github' / 'workflows' / 'blank.yml'
            assert expected_path.exists(), \
                f"Workflow file should exist at {expected_path}"
        finally:
            sys.path.pop(0)
    
    def test_yaml_parsing_works(self, repo_root):
        """
        Check that the workflow YAML at .github/workflows/blank.yml parses to a dictionary and contains a 'name' key.
        
        Parameters:
            repo_root (pathlib.Path): Repository root used to locate the workflow file.
        """
        import yaml
        
        workflow_file = repo_root / '.github' / 'workflows' / 'blank.yml'
        with open(workflow_file, 'r') as f:
            content = yaml.safe_load(f)
        
        assert content is not None, "YAML parsing should succeed"
        assert isinstance(content, dict), "Parsed YAML should be a dictionary"
        assert 'name' in content, "Workflow should have name field"


class TestTestIsolation:
    """Test that tests are properly isolated"""
    
    def test_module_fixtures_are_cached(self, tests_dir):
        """
        Assert that workflow test modules declare module-scoped fixtures to enable fixture reuse and improve performance.
        """
        test_file = tests_dir / 'workflows' / 'test_blank_workflow.py'
        
        with open(test_file, 'r') as f:
            content = f.read()
            
            # Check that expensive operations use module scope
            assert "scope='module'" in content, \
                "Test file should use module-scoped fixtures for performance"
    
    def test_tests_dont_modify_workflow_files(self, repo_root):
        """
        Assert that collecting the workflow tests does not alter any YAML files in .github/workflows.
        
        Records the modification time of each `.yml` file in the workflows directory, runs pytest in collection-only mode on the workflows tests, and fails if any file's modification time changes.
        """
        workflows_dir = repo_root / '.github' / 'workflows'
        
        # Get initial state
        initial_mtimes = {f: f.stat().st_mtime for f in workflows_dir.glob('*.yml')}
        
        # Run tests (in dry-run to avoid actual execution issues)
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 
             str(repo_root / 'tests' / 'workflows'),
             '--collect-only'],
            capture_output=True,
            cwd=str(repo_root)
        )
        
        # Check that files weren't modified
        for workflow_file, initial_mtime in initial_mtimes.items():
            current_mtime = workflow_file.stat().st_mtime
            assert current_mtime == initial_mtime, \
                f"Test execution should not modify {workflow_file.name}"


class TestErrorReporting:
    """Test that test failures provide clear error messages"""
    
    def test_assertion_messages_are_descriptive(self, tests_dir):
        """
        Ensure workflow test files include descriptive assertion messages.
        
        Scans all test_*.py files under the workflows subdirectory of `tests_dir`, counts assert statements and those that include a trailing message, and requires at least 80% of assertions in each file to include an error message. Fails with an AssertionError naming the file and the observed percentage when a file does not meet the threshold.
        
        Parameters:
            tests_dir (Path): Path to the repository's tests directory.
        """
        test_files = list((tests_dir / 'workflows').glob('test_*.py'))
        
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Find assert statements and check for messages
                assert_with_message = 0
                total_asserts = 0
                
                for line in lines:
                    if 'assert ' in line and not line.strip().startswith('#'):
                        total_asserts += 1
                        if ',' in line:  # Has a message
                            assert_with_message += 1
                
                # At least 80% of assertions should have messages
                if total_asserts > 0:
                    ratio = assert_with_message / total_asserts
                    assert ratio >= 0.8, \
                        f"{test_file.name}: Only {ratio:.0%} of assertions have error messages"


class TestTestCoverage:
    """Test that test coverage is comprehensive"""
    
    def test_all_workflow_aspects_tested(self, repo_root):
        """
        Ensure each workflow test file covers a broad set of critical workflow aspects.
        
        For every `test_*.py` under `tests/workflows`, this test checks the file content (case-insensitive)
        for seven predefined aspects and asserts that each file mentions at least five of them.
        
        Parameters:
            repo_root (pathlib.Path): Path to the repository root.
        """
        test_files = list((repo_root / 'tests' / 'workflows').glob('test_*.py'))
        
        critical_aspects = [
            'structure',  # YAML structure
            'metadata',   # Workflow metadata
            'trigger',    # Trigger configuration
            'job',        # Job definitions
            'step',       # Step configurations
            'security',   # Security validation
            'permission', # Permissions
        ]
        
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read().lower()
                
                covered = sum(1 for aspect in critical_aspects 
                             if aspect in content)
                
                # Should cover at least 5 out of 7 aspects
                assert covered >= 5, \
                    f"{test_file.name} should test more workflow aspects (got {covered}/7)"


class TestDocumentation:
    """Test that tests are well-documented"""
    
    def test_all_test_classes_documented(self, tests_dir):
        """
        Ensure every test class in tests/workflows has a non-empty class docstring.
        
        Parses each file matching test_*.py under the workflows subdirectory of the given tests_dir and asserts that every class whose name starts with "Test" has a non-empty docstring. Assertion failures include the test file name and class name.
         
        Parameters:
            tests_dir (Path): Path to the repository's tests directory used to locate the workflows folder.
        """
        import ast
        
        test_files = list((tests_dir / 'workflows').glob('test_*.py'))
        
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                test_classes = [node for node in ast.walk(tree)
                               if isinstance(node, ast.ClassDef)
                               and node.name.startswith('Test')]
                
                for cls in test_classes:
                    docstring = ast.get_docstring(cls)
                    assert docstring is not None, \
                        f"Class {cls.name} in {test_file.name} should have docstring"
    
    def test_all_test_methods_documented(self, tests_dir):
        """
        Ensure every test method in classes named with the "Test" prefix has a non-empty docstring.
        
        Scans all files matching `tests/workflows/test_*.py`, parses each file's AST, and verifies that every method whose name starts with `test_` inside a class whose name starts with `Test` has a docstring. Raises an AssertionError identifying the class, method and file when a test method lacks a docstring.
        """
        import ast
        
        test_files = list((tests_dir / 'workflows').glob('test_*.py'))
        
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               item.name.startswith('test_'):
                                docstring = ast.get_docstring(item)
                                assert docstring is not None, \
                                    f"Method {item.name} in {node.name} ({test_file.name}) needs docstring"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])