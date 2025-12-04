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
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """
    Locate the repository root directory.
    
    Returns:
        Path: The repository root directory (two levels up from this file).
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def tests_root(repo_root):
    """
    Return the path to the repository's tests directory.
    
    Parameters:
        repo_root (Path): Repository root directory.
    
    Returns:
        Path: Path to the `tests` directory inside the repository root.
    """
    return repo_root / 'tests'


@pytest.fixture(scope='module')
def workflows_test_dir(tests_root):
    """
    Locate the workflows subdirectory within the tests directory.
    
    Returns:
        Path: Path to the `tests/workflows` directory.
    """
    return tests_root / 'workflows'


@pytest.fixture(scope='module')
def workflow_files(repo_root):
    """
    Collect all GitHub Actions workflow YAML files from the repository.
    
    Returns:
        list[Path]: Paths to files with `.yml` or `.yaml` extensions located in `.github/workflows`.
    """
    workflows_dir = repo_root / '.github' / 'workflows'
    return list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))


@pytest.fixture(scope='module')
def test_files(workflows_test_dir):
    """
    Collects all test files in the workflows test directory.
    
    Returns:
        list[Path]: A list of Path objects for files in the provided workflows test directory whose names start with `test_` and have a `.py` extension.
    """
    return list(workflows_test_dir.glob('test_*.py'))


class TestTestFileStructure:
    """Validate test file structure and organization"""
    
    def test_all_workflow_files_have_tests(self, workflow_files, test_files):
        """
        Ensure every GitHub workflow file in .github/workflows has a corresponding test file.
        
        Identifies workflow names from `workflow_files` and derives workflow names from `test_files`
        by stripping the `test_` prefix and optional `_workflow` suffix. Recognises these special
        mappings: `jekyll` → `jekyll-gh-pages`, `golangci_lint` → `golangci-lint`,
        `license_check` → `license-check`. Fails the test if any workflow has no matching test.
        
        Parameters:
            workflow_files (iterable[Path]): Paths to workflow YAML files found in .github/workflows.
            test_files (iterable[Path]): Paths to test files in the workflows tests directory.
        """
        workflow_names = {f.stem for f in workflow_files}
        test_workflow_names = set()
        
        for test_file in test_files:
            # Skip meta-test files that don't correspond to workflows
            if test_file.stem in ['test_new_workflow_tests']:
                continue
                
            # Extract workflow name from test file name
            # e.g., test_blank_workflow.py -> blank
            name = test_file.stem.replace('test_', '').replace('_workflow', '')
            test_workflow_names.add(name)
            
            # Add special mappings for workflows with different naming
            if name == 'jekyll':
                test_workflow_names.add('jekyll-gh-pages')
            elif name == 'golangci_lint':
                test_workflow_names.add('golangci-lint')
            elif name == 'license_check':
                test_workflow_names.add('license-check')
        
        missing_tests = workflow_names - test_workflow_names
        assert len(missing_tests) == 0, \
            f"Workflows without tests: {missing_tests}"
    
    def test_no_orphaned_test_files(self, workflow_files, test_files):
        """
        Ensure every workflow test file maps to an existing GitHub workflow file.
        
        Checks each test file in the workflows tests directory and verifies a corresponding workflow filename exists in the repository. Handles underscore-to-dash name variants and a small set of special-name mappings; skips known meta-test files that are not expected to correspond to workflows.
        
        Raises:
        	AssertionError: If a test file has no corresponding workflow file.
        """
        workflow_names = {f.stem for f in workflow_files}
        
        for test_file in test_files:
            # Skip meta-test files that don't correspond to workflows
            if test_file.stem in ['test_new_workflow_tests']:
                continue
                
            # Extract workflow name from test file name
            name = test_file.stem.replace('test_', '').replace('_workflow', '')
            # Handle both 'name.yml' and 'name-with-dashes.yml' patterns
            possible_names = [name, name.replace('_', '-')]
            
            # Special cases for specific workflow mappings
            if name == 'jekyll':
                possible_names.extend(['jekyll-gh-pages'])
            elif name == 'golangci_lint':
                possible_names.extend(['golangci-lint'])
            elif name == 'license_check':
                possible_names.extend(['license-check'])
            
            has_corresponding_workflow = any(wf in workflow_names for wf in possible_names)
            assert has_corresponding_workflow, \
                f"Test file {test_file.name} has no corresponding workflow"
    
    def test_all_test_files_are_python(self, test_files):
        """Test that all test files have .py extension"""
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
        """
        Ensure each test file contains a module-level docstring and that the docstring is longer than 50 characters.
        
        Parameters:
            test_files (list[Path]): Iterable of test file paths to validate.
        """
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
        """Test that all test files import pytest"""
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'import pytest' in content, \
                    f"Test file {test_file.name} should import pytest"
    
    def test_all_test_files_import_yaml(self, test_files):
        """Test that workflow test files import yaml for parsing"""
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
        Verify each test file contains a definition for a `workflow_path` fixture.
        
        Fails with an AssertionError naming the file when a test file does not define `def workflow_path()`.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'def workflow_path()' in content, \
                    f"Test file {test_file.name} should define workflow_path fixture"
    
    def test_workflow_content_fixture_exists(self, test_files):
        """Test that all test files define workflow_content fixture"""
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'def workflow_content(' in content, \
                    f"Test file {test_file.name} should define workflow_content fixture"
    
    def test_fixtures_use_module_scope(self, test_files):
        """
        Ensure specific expensive fixtures are declared with module scope.
        
        Parameters:
            test_files (list[Path]): List of test file paths to inspect for fixture definitions.
        
        Raises:
            AssertionError: If a fixture named `workflow_path`, `workflow_raw`, `workflow_content` or `jobs`
            exists but is not declared with `scope='module'` in its `pytest.fixture` decorator.
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
        """Test that all test methods follow test_* naming convention"""
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               not item.name.startswith('_'):
                                # Check if it's a pytest fixture
                                is_fixture = any(
                                    (hasattr(d, 'id') and d.id == 'pytest' and 
                                     hasattr(d, 'attr') and d.attr == 'fixture') or
                                    (hasattr(d, 'attr') and d.attr == 'fixture')
                                    for d in item.decorator_list
                                )
                                if not is_fixture:
                                    assert item.name.startswith('test_'), \
                                        f"Method {item.name} in {node.name} should start with 'test_'"
    
    def test_test_methods_have_docstrings(self, test_files):
        """Test that all test methods have descriptive docstrings"""
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
        """
        Ensure test method names are descriptive by requiring at least three underscore-separated parts.
        
        Iterates Test* classes in each provided test file and asserts each `test_*` method name contains at least three parts when split on `_` (for example, `test_verb_noun_context`). Fails with a message naming the offending test and file when a name is too short.
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
                                # Name should have at least 3 parts (test_verb_noun_context)
                                parts = item.name.split('_')
                                assert len(parts) >= 3, \
                                    f"Test name {item.name} in {test_file.name} should be more descriptive"


class TestTestOrganization:
    """Validate test organization and grouping"""
    
    def test_tests_grouped_by_functionality(self, test_files):
        """
        Ensure each test file groups tests into multiple Test* classes representing distinct functionality.
        
        Raises:
        	AssertionError: if a test file contains fewer than three classes whose names start with `Test`; the assertion message includes the filename.
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
        Assert that each provided test file contains at least two of a set of common Test* classes.
        
        Checks for the presence of the following class names in each file: TestWorkflowStructure, TestWorkflowMetadata, TestWorkflowSecurity, TestEdgeCases. Raises an assertion error if fewer than two of these classes are found in a file.
        
        Parameters:
            test_files (list[pathlib.Path]): Iterable of test file paths to inspect.
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
        """Test that all test files validate YAML structure"""
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'yaml' in content.lower() or 'YAML' in content, \
                    f"Test file {test_file.name} should validate YAML structure"
    
    def test_tests_validate_workflow_metadata(self, test_files):
        """Test that all test files validate workflow metadata"""
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                # Should test workflow name
                assert 'name' in content and 'workflow' in content.lower(), \
                    f"Test file {test_file.name} should validate workflow metadata"
    
    def test_tests_validate_security(self, test_files):
        """
        Ensure each test file contains security-related checks.
        
        Searches the file for any of the case-insensitive keywords: 'security', 'permission', 'token', 'secret'.
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
        Verify each test file mentions edge-case testing.
        
        Asserts that every file in the provided collection contains the substring "edge" (case-insensitive) to indicate the presence of edge-case tests.
        """
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                assert 'edge' in content.lower() or 'Edge' in content, \
                    f"Test file {test_file.name} should include edge case testing"


class TestREADMEAccuracy:
    """Validate that README accurately documents the test suite"""
    
    def test_readme_exists(self, tests_root):
        """
        Verify the repository's tests/README.md file exists.
        """
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
        Verify the tests/README.md documents commands to run the test suite.
        
        Checks that the README contains references to 'pytest' and to 'python' or 'python3'.
        """
        readme = tests_root / 'README.md'
        with open(readme, 'r') as f:
            content = f.read()
            
            assert 'pytest' in content.lower(), \
                "README should include pytest run instructions"
            assert 'python' in content.lower() or 'python3' in content.lower(), \
                "README should include Python run instructions"
    
    def test_readme_documents_dependencies(self, tests_root):
        """
        Verify that tests/README.md mentions test dependencies.
        
        Checks that the README.md file in the tests directory contains either the word "dependencies" or "requirements" (case-insensitive).
        
        Parameters:
            tests_root (Path): Path to the repository's tests directory.
        """
        readme = tests_root / 'README.md'
        with open(readme, 'r') as f:
            content = f.read()
            
            assert 'dependencies' in content.lower() or 'requirements' in content.lower(), \
                "README should document test dependencies"


class TestTestInfrastructure:
    """Validate test infrastructure files"""
    
    def test_pytest_ini_exists(self, repo_root):
        """
        Verify the repository root contains a pytest.ini file.
        Ensures repository-level pytest configuration is present so tests run with the expected settings.
        """
        pytest_ini = repo_root / 'pytest.ini'
        assert pytest_ini.exists(), "pytest.ini should exist"
    
    def test_requirements_txt_exists(self, tests_root):
        """Test that tests/requirements.txt exists"""
        requirements = tests_root / 'requirements.txt'
        assert requirements.exists(), "tests/requirements.txt should exist"
    
    def test_requirements_includes_pytest(self, tests_root):
        """
        Verify that tests/requirements.txt lists pytest.
        
        Performs a case-insensitive check for the string 'pytest' in the requirements file.
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
        """Test that __init__.py files exist for proper package structure"""
        assert (tests_root / '__init__.py').exists(), \
            "tests/__init__.py should exist"
        assert (workflows_test_dir / '__init__.py').exists(), \
            "tests/workflows/__init__.py should exist"


class TestCodeQuality:
    """Validate code quality in test files"""
    
    def test_no_syntax_errors(self, test_files):
        """
        Assert that each file in `test_files` contains valid Python syntax.
        
        Parameters:
            test_files (list[Path]): Iterable of file paths to test; each file will be parsed for syntax validity.
        
        Notes:
            The test will fail for the first file that raises a SyntaxError.
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
        Detects obvious unused imports in the provided test files.
        
        Asserts that any file importing `from pathlib import Path` also contains either `Path(` or `Path.`; raises an assertion error naming the file when this condition is not met.
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
        Verify non-empty, non-comment lines use indentation aligned to 4 spaces.
        
        Raises:
            AssertionError: If a line has leading spaces that are not a multiple of four; the error message includes the file name and line number.
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
        Ensure each test file contains a minimum number of test methods.
        
        Counts functions whose names start with `test_` inside classes whose names start with `Test` and asserts each file has at least 20 such test methods; the assertion message includes the file name and actual count.
        
        Parameters:
            test_files (Iterable[Path]): Paths to test files to validate.
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
        Ensure each test file contains at least five test classes whose names start with 'Test'.
        
        Raises an AssertionError naming the offending file if fewer than five such classes are found.
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