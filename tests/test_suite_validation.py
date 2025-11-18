"""
Meta-test suite for validating the Symphonic-Joules test infrastructure.

This test suite validates the test suite itself, ensuring:
- Test files follow pytest conventions
- Test structure is consistent across files
- Fixtures are properly scoped and used
- Documentation is complete and accurate
- All workflow files have corresponding tests
- Test naming conventions are followed
- Module structure is correct
"""

import pytest
import ast
import yaml
import os
from pathlib import Path
from typing import List, Set, Dict


@pytest.fixture(scope='module')
def repo_root():
    """
    Return the repository root directory.
    
    Returns:
        Path: Path to the repository root directory.
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def tests_root(repo_root):
    """
    Return the repository's tests directory path.
    
    Parameters:
        repo_root (Path): Root path of the repository.
    
    Returns:
        Path: Path to the `tests` directory under the repository root.
    """
    return repo_root / 'tests'


@pytest.fixture(scope='module')
def workflows_test_dir(tests_root):
    """
    Return the path to the workflows tests subdirectory.
    
    Parameters:
        tests_root (Path | str): Path to the repository's `tests` directory.
    
    Returns:
        Path: Path to the `tests/workflows` directory.
    """
    return tests_root / 'workflows'


@pytest.fixture(scope='module')
def workflow_files(repo_root):
    """
    Return the workflow YAML files located in the repository's .github/workflows directory.
    
    Parameters:
        repo_root (Path): Path to the repository root.
    
    Returns:
        List[Path]: All files with `.yml` or `.yaml` extensions found in `.github/workflows` under `repo_root`.
    """
    workflows_dir = repo_root / '.github' / 'workflows'
    return list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))


@pytest.fixture(scope='module')
def test_files(workflows_test_dir):
    """
    Collect all test files in the workflows test directory.
    
    Parameters:
        workflows_test_dir (Path): Path to the tests/workflows directory.
    
    Returns:
        list[Path]: List of Path objects for files matching `test_*.py` in the directory.
    """
    return list(workflows_test_dir.glob('test_*.py'))


class TestTestFileStructure:
    """Validate test file structure and organization"""
    
    def test_all_workflow_files_have_tests(self, workflow_files, test_files):
        """Test that every workflow file has a corresponding test file"""
        workflow_names = {f.stem for f in workflow_files}
        test_workflow_names = set()
        
        for test_file in test_files:
            # Extract workflow name from test file name
            # e.g., test_blank_workflow.py -> blank
            name = test_file.stem.replace('test_', '').replace('_workflow', '')
            test_workflow_names.add(name)
        
        missing_tests = workflow_names - test_workflow_names
        assert len(missing_tests) == 0, \
            f"Workflows without tests: {missing_tests}"
    
    def test_no_orphaned_test_files(self, workflow_files, test_files):
        """Test that there are no test files without corresponding workflows"""
        workflow_names = {f.stem for f in workflow_files}
        
        for test_file in test_files:
            # Extract workflow name from test file name
            name = test_file.stem.replace('test_', '').replace('_workflow', '')
            # Handle both 'name.yml' and 'name-with-dashes.yml' patterns
            possible_names = [name, name.replace('_', '-')]
            
            has_corresponding_workflow = any(wf in workflow_names for wf in possible_names)
            assert has_corresponding_workflow, \
                f"Test file {test_file.name} has no corresponding workflow"
    
    def test_all_test_files_are_python(self, test_files):
        """
        Verify every collected test file uses the .py file extension.
        
        Parameters:
            test_files (Iterable[Path]): An iterable of file paths for test files to validate.
        """
        for test_file in test_files:
            assert test_file.suffix == '.py', \
                f"Test file {test_file.name} should have .py extension"
    
    def test_all_test_files_start_with_test(self, test_files):
        """Test that all test files follow test_*.py naming convention"""
        for test_file in test_files:
            assert test_file.stem.startswith('test_'), \
                f"Test file {test_file.name} should start with 'test_'"


class TestTestFileContent:
    """Validate content and structure within test files"""
    
    def test_all_test_files_have_docstrings(self, test_files):
        """Test that all test files have module-level docstrings"""
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                docstring = ast.get_docstring(tree)
                
                assert docstring is not None, \
                    f"Test file {test_file.name} missing module docstring"
                assert len(docstring) > 50, \
                    f"Test file {test_file.name} docstring too short"
    
    def test_all_test_files_import_pytest(self, test_files):
        """
        Ensure every test file contains an `import pytest` statement.
        
        Fails the test if any file in `test_files` does not include the literal `import pytest`.
        
        Parameters:
            test_files (Iterable[Path]): Paths of the test files to validate.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'import pytest' in content, \
                    f"Test file {test_file.name} should import pytest"
    
    def test_all_test_files_import_yaml(self, test_files):
        """
        Verify each workflow test file imports the yaml module.
        
        Raises an AssertionError if any file does not contain the literal string 'import yaml'.
        
        Parameters:
            test_files (Iterable[Path]): Paths of test files to inspect.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'import yaml' in content, \
                    f"Test file {test_file.name} should import yaml"
    
    def test_all_test_files_have_test_classes(self, test_files):
        """Test that all test files contain test classes"""
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                test_classes = [node for node in ast.walk(tree) 
                               if isinstance(node, ast.ClassDef) 
                               and node.name.startswith('Test')]
                
                assert len(test_classes) > 0, \
                    f"Test file {test_file.name} has no test classes"
    
    def test_test_classes_have_docstrings(self, test_files):
        """Test that all test classes have docstrings"""
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
                        f"Test class {cls.name} in {test_file.name} missing docstring"


class TestFixtureUsage:
    """Validate fixture definitions and usage patterns"""
    
    def test_workflow_path_fixture_exists(self, test_files):
        """
        Verify each test file defines a `workflow_path` fixture.
        
        Parameters:
            test_files (Iterable[Path]): Paths of test files to check.
        
        Notes:
            Asserts that each file contains a top-level `def workflow_path()` definition.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'def workflow_path()' in content, \
                    f"Test file {test_file.name} should define workflow_path fixture"
    
    def test_workflow_content_fixture_exists(self, test_files):
        """
        Require each test file to define a `workflow_content` fixture.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'def workflow_content(' in content, \
                    f"Test file {test_file.name} should define workflow_content fixture"
    
    def test_fixtures_use_module_scope(self, test_files):
        """
        Verify that expensive fixtures use module scope.
        
        Checks test files to ensure fixtures named `workflow_path`, `workflow_raw`,
        `workflow_content`, and `jobs` are declared with `scope='module'`. Raises an
        AssertionError when one of these fixtures is present but does not specify
        module scope.
        
        Parameters:
            test_files (Iterable[Path]): Paths to test files to inspect.
        
        Raises:
            AssertionError: If a required fixture exists in a test file but is not
                declared with `scope='module'`.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if function has pytest.fixture decorator
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Call):
                                if hasattr(decorator.func, 'attr') and \
                                   decorator.func.attr == 'fixture':
                                    # Check for scope parameter
                                    fixture_name = node.name
                                    if fixture_name in ['workflow_path', 'workflow_raw', 
                                                       'workflow_content', 'jobs']:
                                        # These should be module-scoped
                                        has_module_scope = any(
                                            isinstance(kw, ast.keyword) and 
                                            kw.arg == 'scope' and
                                            isinstance(kw.value, ast.Constant) and
                                            kw.value.value == 'module'
                                            for kw in decorator.keywords
                                        )
                                        assert has_module_scope, \
                                            f"Fixture {fixture_name} in {test_file.name} should use module scope"


class TestTestMethodNaming:
    """Validate test method naming conventions"""
    
    def test_all_test_methods_start_with_test(self, test_files):
        """
        Enforces that every public test method in classes prefixed with `Test` is named with the `test_` prefix.
        
        Parses each file in `test_files` and asserts that for every class whose name starts with `Test`, every method that does not start with an underscore begins with `test_`.
        
        Parameters:
            test_files (Iterable[pathlib.Path | str]): Iterable of file paths to test modules to validate.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               not item.name.startswith('_'):
                                assert item.name.startswith('test_'), \
                                    f"Method {item.name} in {node.name} should start with 'test_'"
    
    def test_test_methods_have_docstrings(self, test_files):
        """
        Verify every test method defined in classes whose names start with `Test` has a docstring.
        
        Parameters:
            test_files (Iterable[Path]): Paths to test files to inspect.
        
        Raises:
            AssertionError: If any `test_` method in a `Test*` class is missing a docstring.
        """
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
                                    f"Test method {item.name} in {node.name} ({test_file.name}) missing docstring"
    
    def test_test_names_are_descriptive(self, test_files):
        """Test that test method names are sufficiently descriptive"""
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               item.name.startswith('test_'):
                                # Name should have at least 3 parts (test_verb_noun_context)
                                parts = item.name.split('_')
                                assert len(parts) >= 3, \
                                    f"Test name {item.name} in {test_file.name} should be more descriptive"


class TestTestOrganization:
    """Validate test organization and grouping"""
    
    def test_tests_grouped_by_functionality(self, test_files):
        """
        Verify each test file groups tests into multiple Test* classes for functionality separation.
        
        Asserts that every file in `test_files` defines at least three top-level classes whose names start with `Test`.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                test_classes = [node for node in ast.walk(tree) 
                               if isinstance(node, ast.ClassDef) 
                               and node.name.startswith('Test')]
                
                # Should have multiple test classes for organization
                assert len(test_classes) >= 3, \
                    f"Test file {test_file.name} should have multiple test classes for organization"
    
    def test_common_test_classes_exist(self, test_files):
        """
        Verify each test file defines at least two of the common test class names: TestWorkflowStructure, TestWorkflowMetadata, TestWorkflowSecurity, TestEdgeCases.
        
        Parameters:
            test_files (Iterable[Path]): Paths to test files to inspect.
        """
        common_classes = [
            'TestWorkflowStructure',
            'TestWorkflowMetadata',
            'TestWorkflowSecurity',
            'TestEdgeCases'
        ]
        
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                class_names = [node.name for node in ast.walk(tree) 
                              if isinstance(node, ast.ClassDef)]
                
                # Should have at least 2 of the common test classes
                common_found = sum(1 for cls in common_classes if cls in class_names)
                assert common_found >= 2, \
                    f"Test file {test_file.name} should include common test classes"


class TestTestCoverage:
    """Validate test coverage completeness"""
    
    def test_tests_validate_yaml_structure(self, test_files):
        """
        Require each test file to reference YAML parsing or validation.
        
        Checks that every file in `test_files` contains the token "yaml" in any casing; fails if a test file lacks a YAML-related reference.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'yaml' in content.lower() or 'YAML' in content, \
                    f"Test file {test_file.name} should validate YAML structure"
    
    def test_tests_validate_workflow_metadata(self, test_files):
        """
        Ensure each test file contains checks for workflow name and metadata keywords.
        
        Verifies every file in `test_files` references the 'name' key and the term 'workflow' (case-insensitive) to confirm workflow metadata is validated.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                # Should test workflow name
                assert 'name' in content and 'workflow' in content.lower(), \
                    f"Test file {test_file.name} should validate workflow metadata"
    
    def test_tests_validate_security(self, test_files):
        """
        Verify each file in `test_files` contains at least one security-related keyword.
        
        Parameters:
            test_files (Iterable[Path]): An iterable of file paths for test files to scan for security-related keywords such as "security", "permission", "token" or "secret".
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                security_keywords = ['security', 'permission', 'token', 'secret']
                has_security_test = any(keyword in content.lower() 
                                       for keyword in security_keywords)
                assert has_security_test, \
                    f"Test file {test_file.name} should include security validation"
    
    def test_tests_validate_edge_cases(self, test_files):
        """
        Ensure each test file references edge cases.
        
        Parameters:
            test_files (Iterable[Path]): Iterable of test file paths to check for edge-case coverage.
        
        Raises:
            AssertionError: If a test file does not contain the substring "edge" (case-insensitive).
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'edge' in content.lower() or 'Edge' in content, \
                    f"Test file {test_file.name} should include edge case testing"


class TestREADMEAccuracy:
    """Validate that README accurately documents the test suite"""
    
    def test_readme_exists(self, tests_root):
        """Test that tests/README.md exists"""
        readme = tests_root / 'README.md'
        assert readme.exists(), "tests/README.md should exist"
    
    def test_readme_documents_all_test_files(self, tests_root, test_files):
        """Test that README mentions all test files"""
        readme = tests_root / 'README.md'
        with open(readme, 'r') as f:
            content = f.read()
            
            for test_file in test_files:
                assert test_file.name in content, \
                    f"README should document {test_file.name}"
    
    def test_readme_has_run_instructions(self, tests_root):
        """
        Verify tests/README.md documents how to run the test suite.
        
        Checks that the README contains the keyword `pytest` and either `python` or `python3`.
        """
        readme = tests_root / 'README.md'
        with open(readme, 'r') as f:
            content = f.read()
            
            assert 'pytest' in content.lower(), \
                "README should include pytest run instructions"
            assert 'python' in content.lower() or 'python3' in content.lower(), \
                "README should include Python run instructions"
    
    def test_readme_documents_dependencies(self, tests_root):
        """Test that README documents test dependencies"""
        readme = tests_root / 'README.md'
        with open(readme, 'r') as f:
            content = f.read()
            
            assert 'dependencies' in content.lower() or 'requirements' in content.lower(), \
                "README should document test dependencies"


class TestTestInfrastructure:
    """Validate test infrastructure files"""
    
    def test_pytest_ini_exists(self, repo_root):
        """Test that pytest.ini exists for test configuration"""
        pytest_ini = repo_root / 'pytest.ini'
        assert pytest_ini.exists(), "pytest.ini should exist"
    
    def test_requirements_txt_exists(self, tests_root):
        """Test that tests/requirements.txt exists"""
        requirements = tests_root / 'requirements.txt'
        assert requirements.exists(), "tests/requirements.txt should exist"
    
    def test_requirements_includes_pytest(self, tests_root):
        """
        Verify tests/requirements.txt lists pytest as a dependency.
        
        Checks the file case-insensitively and fails the test if 'pytest' is not present.
        """
        requirements = tests_root / 'requirements.txt'
        with open(requirements, 'r') as f:
            content = f.read()
            assert 'pytest' in content.lower(), \
                "requirements.txt should include pytest"
    
    def test_requirements_includes_yaml(self, tests_root):
        """Test that requirements.txt includes PyYAML"""
        requirements = tests_root / 'requirements.txt'
        with open(requirements, 'r') as f:
            content = f.read()
            assert 'yaml' in content.lower(), \
                "requirements.txt should include PyYAML"
    
    def test_init_files_exist(self, tests_root, workflows_test_dir):
        """
        Verify that package initialiser files exist at tests/__init__.py and tests/workflows/__init__.py to ensure proper package structure.
        """
        assert (tests_root / '__init__.py').exists(), \
            "tests/__init__.py should exist"
        assert (workflows_test_dir / '__init__.py').exists(), \
            "tests/workflows/__init__.py should exist"


class TestCodeQuality:
    """Validate code quality in test files"""
    
    def test_no_syntax_errors(self, test_files):
        """
        Verify each collected test file parses as valid Python source.
        
        Fails the test if any file raises a SyntaxError when parsed with the AST parser.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {test_file.name}: {e}")
    
    def test_no_unused_imports(self, test_files):
        """
        Ensure test files do not import `Path` from `pathlib` without using it.
        
        Scans each test file for the literal import `from pathlib import Path` and asserts that `Path(` or `Path.` appears in the file; raises an assertion error identifying the file when the import is present but not used.
        """
        # This is a simplified check - full unused import detection requires more complex analysis
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                
                # Check if Path is imported but never used
                if 'from pathlib import Path' in content:
                    # Path should be used somewhere
                    assert 'Path(' in content or 'Path.' in content, \
                        f"Path imported but not used in {test_file.name}"
    
    def test_consistent_indentation(self, test_files):
        """
        Fail the test if any non-empty, non-comment line in the given test files uses indentation that is not a multiple of four spaces.
        
        Checks each file line-by-line, ignores blank lines and lines that start with `#`, and asserts that any leading space count is either zero or divisible by four. The assertion message includes the file name and line number on failure.
        
        Parameters:
            test_files (List[pathlib.Path]): Iterable of file paths for test files to validate indentation for.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    if line.strip() and not line.strip().startswith('#'):
                        leading = len(line) - len(line.lstrip(' '))
                        if leading > 0:
                            assert leading % 4 == 0, \
                                f"Inconsistent indentation in {test_file.name} line {i}"


class TestTestCompleteness:
    """Validate completeness of test coverage"""
    
    def test_sufficient_test_count(self, test_files):
        """
        Ensure each test file defines at least 20 test methods.
        
        Counts functions whose names start with `test_` inside classes whose names start with `Test` and fails the test if a file has fewer than 20 such methods.
        
        Parameters:
            test_files (Iterable[Path]): Iterable of test file paths to validate.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                test_methods = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               item.name.startswith('test_'):
                                test_methods.append(item.name)
                
                # Each test file should have at least 20 tests for comprehensive coverage
                assert len(test_methods) >= 20, \
                    f"Test file {test_file.name} has only {len(test_methods)} tests, should have at least 20"
    
    def test_minimum_test_classes(self, test_files):
        """
        Require each test file to define at least five `Test*` classes to ensure tests are organised.
        
        Parameters:
            test_files (Iterable[Path]): Iterable of paths to test files to validate.
        
        Raises:
            AssertionError: If any test file contains fewer than five classes whose names start with `Test`.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                test_classes = [node for node in ast.walk(tree) 
                               if isinstance(node, ast.ClassDef) 
                               and node.name.startswith('Test')]
                
                # Should have at least 5 test classes for good organization
                assert len(test_classes) >= 5, \
                    f"Test file {test_file.name} should have at least 5 test classes"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])