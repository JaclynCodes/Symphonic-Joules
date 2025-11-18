"""
Validation tests for newly added workflow test files.

This module specifically tests the new test files added in this branch:
- test_jekyll_workflow.py
- test_static_workflow.py

It validates that these new files:
- Follow established patterns from test_blank_workflow.py
- Have comprehensive test coverage
- Use proper fixture patterns
- Include all necessary test categories
- Have consistent structure and documentation
"""

import pytest
import ast
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """
    Return the repository root path.
    
    Returns:
        Path: Path to the repository root directory.
    """
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope='module')
def workflows_test_dir(repo_root):
    """
    Locate the tests/workflows directory under the repository root.
    
    Parameters:
    	repo_root (Path): Path to the repository root.
    
    Returns:
    	Path: Path to the tests/workflows directory.
    """
    return repo_root / 'tests' / 'workflows'


@pytest.fixture(scope='module')
def jekyll_test_file(workflows_test_dir):
    """
    Locate the Jekyll workflow test file within the workflows test directory.
    
    Parameters:
        workflows_test_dir (Path): Path to the directory containing workflow test files.
    
    Returns:
        Path: Path to 'test_jekyll_workflow.py' inside the provided directory.
    """
    return workflows_test_dir / 'test_jekyll_workflow.py'


@pytest.fixture(scope='module')
def static_test_file(workflows_test_dir):
    """
    Resolve the path to the static workflow test file within the workflows test directory.
    
    Returns:
    	Path to tests/workflows/test_static_workflow.py
    """
    return workflows_test_dir / 'test_static_workflow.py'


@pytest.fixture(scope='module')
def blank_test_file(workflows_test_dir):
    """
    Locate the reference blank workflow test file within the workflows tests directory.
    
    Parameters:
        workflows_test_dir (Path): Path to the tests/workflows directory.
    
    Returns:
        Path: Path to tests/workflows/test_blank_workflow.py
    """
    return workflows_test_dir / 'test_blank_workflow.py'


class TestNewFilesExist:
    """Test that new test files exist"""
    
    def test_jekyll_test_file_exists(self, jekyll_test_file):
        """Test that test_jekyll_workflow.py exists"""
        assert jekyll_test_file.exists(), \
            "test_jekyll_workflow.py should exist"
    
    def test_static_test_file_exists(self, static_test_file):
        """Test that test_static_workflow.py exists"""
        assert static_test_file.exists(), \
            "test_static_workflow.py should exist"
    
    def test_both_files_are_python(self, jekyll_test_file, static_test_file):
        """Test that both new files have .py extension"""
        assert jekyll_test_file.suffix == '.py', \
            "Jekyll test file should be Python"
        assert static_test_file.suffix == '.py', \
            "Static test file should be Python"


class TestNewFilesFollowPattern:
    """Test that new files follow established patterns"""
    
    def test_new_files_have_module_docstrings(self, jekyll_test_file, static_test_file):
        """Test that new files have comprehensive module docstrings"""
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                docstring = ast.get_docstring(tree)
                
                assert docstring is not None, \
                    f"{test_file.name} should have module docstring"
                assert len(docstring) > 100, \
                    f"{test_file.name} docstring should be comprehensive"
    
    def test_new_files_import_same_modules(self, jekyll_test_file, static_test_file, blank_test_file):
        """
        Verify that both new workflow test files import the expected core modules.
        
        Asserts that each of test_jekyll_workflow.py and test_static_workflow.py contains imports for: `pytest`, `yaml`, `os` and `Path`.
        """
        # Get imports from blank test file (reference)
        with open(blank_test_file, 'r') as f:
            blank_content = f.read()
        
        required_imports = ['pytest', 'yaml', 'os', 'Path']
        
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                for imp in required_imports:
                    assert imp in content, \
                        f"{test_file.name} should import {imp}"
    
    def test_new_files_use_module_scoped_fixtures(self, jekyll_test_file, static_test_file):
        """Test that new files use module-scoped fixtures like blank test"""
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert "scope='module'" in content, \
                    f"{test_file.name} should use module-scoped fixtures"
    
    def test_new_files_have_workflow_path_fixture(self, jekyll_test_file, static_test_file):
        """
        Verify each new workflow test file defines a top-level `workflow_path` fixture.
        
        Raises:
        	AssertionError: If any of the provided test files does not contain a `def workflow_path()` declaration.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'def workflow_path()' in content, \
                    f"{test_file.name} should define workflow_path fixture"
    
    def test_new_files_have_workflow_content_fixture(self, jekyll_test_file, static_test_file):
        """
        Verify that both new workflow test files define a `workflow_content` fixture.
        
        Asserts each file's source contains a function definition for `workflow_content`.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'def workflow_content(' in content, \
                    f"{test_file.name} should define workflow_content fixture"


class TestJekyllTestFileStructure:
    """Test Jekyll workflow test file structure"""
    
    def test_jekyll_has_sufficient_test_classes(self, jekyll_test_file):
        """
        Assert the Jekyll workflow test file defines at least 10 top-level test classes.
        
        Each counted class is a class definition whose name starts with "Test"; the test fails if fewer than 10 such classes are present.
        """
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
            
            test_classes = [node for node in ast.walk(tree)
                           if isinstance(node, ast.ClassDef)
                           and node.name.startswith('Test')]
            
            assert len(test_classes) >= 10, \
                f"Jekyll test should have at least 10 test classes (got {len(test_classes)})"
    
    def test_jekyll_has_sufficient_tests(self, jekyll_test_file):
        """
        Verify the Jekyll test file defines at least 50 test methods across classes named with the "Test" prefix.
        
        Parameters:
            jekyll_test_file (Path | str): Path to the test_jekyll_workflow.py file to inspect.
        
        Raises:
            AssertionError: If fewer than 50 methods whose names start with "test_" are found in classes whose names start with "Test".
        """
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
            
            test_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and \
                           item.name.startswith('test_'):
                            test_count += 1
            
            assert test_count >= 50, \
                f"Jekyll test should have at least 50 tests (got {test_count})"
    
    def test_jekyll_tests_build_and_deploy_jobs(self, jekyll_test_file):
        """
        Verify the Jekyll test file defines test classes for both the build and deploy jobs.
        
        Asserts that the file content contains the identifiers `TestBuildJob` and `TestDeployJob`.
        """
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            
            assert 'TestBuildJob' in content, \
                "Jekyll test should have TestBuildJob class"
            assert 'TestDeployJob' in content, \
                "Jekyll test should have TestDeployJob class"
    
    def test_jekyll_tests_permissions(self, jekyll_test_file):
        """Test that Jekyll test file validates permissions"""
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            
            assert 'TestPermissionsConfiguration' in content, \
                "Jekyll test should validate permissions"
            assert 'id-token' in content, \
                "Jekyll test should validate OIDC (id-token)"
    
    def test_jekyll_tests_concurrency(self, jekyll_test_file):
        """
        Verify the Jekyll workflow test file includes concurrency-related tests.
        
        Asserts that the file contains a TestConcurrencyConfiguration class and that it checks the `cancel-in-progress` concurrency setting.
        """
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            
            assert 'TestConcurrencyConfiguration' in content, \
                "Jekyll test should validate concurrency"
            assert 'cancel-in-progress' in content, \
                "Jekyll test should check cancel-in-progress setting"


class TestStaticTestFileStructure:
    """Test static workflow test file structure"""
    
    def test_static_has_sufficient_test_classes(self, static_test_file):
        """
        Verify the static workflow test file defines at least 10 test classes whose names start with "Test".
        
        Asserts that the AST of the provided file contains 10 or more class definitions with names beginning with "Test"; fails with a descriptive message if the requirement is not met.
        """
        with open(static_test_file, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
            
            test_classes = [node for node in ast.walk(tree)
                           if isinstance(node, ast.ClassDef)
                           and node.name.startswith('Test')]
            
            assert len(test_classes) >= 10, \
                f"Static test should have at least 10 test classes (got {len(test_classes)})"
    
    def test_static_has_sufficient_tests(self, static_test_file):
        """
        Verify the static workflow test file defines at least 50 test methods across classes whose names start with "Test".
        
        Counts functions with names beginning with "test_" inside top-level classes prefixed with "Test" and fails the test if the total is less than 50.
        """
        with open(static_test_file, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
            
            test_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and \
                           item.name.startswith('test_'):
                            test_count += 1
            
            assert test_count >= 50, \
                f"Static test should have at least 50 tests (got {test_count})"
    
    def test_static_tests_single_job_architecture(self, static_test_file):
        """Test that static test validates single job architecture"""
        with open(static_test_file, 'r') as f:
            content = f.read()
            
            # Static workflow has single deploy job (no separate build)
            assert 'TestDeployJob' in content or 'deploy' in content.lower(), \
                "Static test should validate deploy job"
    
    def test_static_tests_permissions(self, static_test_file):
        """Test that static test file validates permissions"""
        with open(static_test_file, 'r') as f:
            content = f.read()
            
            assert 'TestPermissionsConfiguration' in content, \
                "Static test should validate permissions"
            assert 'pages' in content and 'write' in content, \
                "Static test should validate pages write permission"
    
    def test_static_compares_with_jekyll(self, static_test_file):
        """
        Verify the static workflow test file contains a comparison to the Jekyll workflow.
        
        Asserts that the file content includes one of the comparison indicators: the substring "Jekyll", the class name "TestWorkflowDifferences", or the phrase "single job" (case-insensitive).
        """
        with open(static_test_file, 'r') as f:
            content = f.read()
            
            # Should have test class comparing differences
            has_comparison = 'Jekyll' in content or \
                           'TestWorkflowDifferences' in content or \
                           'single job' in content.lower()
            
            assert has_comparison, \
                "Static test should compare with Jekyll workflow"


class TestCommonTestPatterns:
    """Test that both new files include common test patterns"""
    
    def test_both_validate_yaml_structure(self, jekyll_test_file, static_test_file):
        """Test that both files validate YAML structure"""
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestWorkflowStructure' in content, \
                    f"{test_file.name} should have TestWorkflowStructure class"
    
    def test_both_validate_metadata(self, jekyll_test_file, static_test_file):
        """Test that both files validate workflow metadata"""
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestWorkflowMetadata' in content, \
                    f"{test_file.name} should have TestWorkflowMetadata class"
    
    def test_both_validate_security(self, jekyll_test_file, static_test_file):
        """
        Verify both workflow test files declare a TestWorkflowSecurity test class.
        
        Checks each provided test file for a top-level TestWorkflowSecurity class definition and fails the test if it is missing.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestWorkflowSecurity' in content, \
                    f"{test_file.name} should have TestWorkflowSecurity class"
    
    def test_both_test_edge_cases(self, jekyll_test_file, static_test_file):
        """
        Assert that both workflow test files include a TestEdgeCases test class.
        
        Parameters:
            jekyll_test_file (Path): Path to the Jekyll workflow test file.
            static_test_file (Path): Path to the Static workflow test file.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestEdgeCases' in content, \
                    f"{test_file.name} should have TestEdgeCases class"
    
    def test_both_validate_file_permissions(self, jekyll_test_file, static_test_file):
        """
        Verify both workflow test files define a TestWorkflowFilePermissions class.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestWorkflowFilePermissions' in content, \
                    f"{test_file.name} should have TestWorkflowFilePermissions class"


class TestCodeQuality:
    """Test code quality in new test files"""
    
    def test_no_syntax_errors(self, jekyll_test_file, static_test_file):
        """Test that new files have no syntax errors"""
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {test_file.name}: {e}")
    
    def test_all_test_methods_have_docstrings(self, jekyll_test_file, static_test_file):
        """
        Verify every test method in the Jekyll and Static workflow test files has a docstring.
        
        Parses each provided test file, inspects classes whose names start with "Test" and their methods whose names start with "test_", and fails the test if any such method lacks a docstring. The assertion message includes up to five example method names missing docstrings.
        
        Parameters:
            jekyll_test_file (Path): Path to the Jekyll workflow test file to inspect.
            static_test_file (Path): Path to the Static workflow test file to inspect.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                missing_docstrings = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               item.name.startswith('test_'):
                                if ast.get_docstring(item) is None:
                                    missing_docstrings.append(f"{node.name}.{item.name}")
                
                assert len(missing_docstrings) == 0, \
                    f"{test_file.name} has test methods without docstrings: {missing_docstrings[:5]}"
    
    def test_consistent_indentation(self, jekyll_test_file, static_test_file):
        """
        Verify that both workflow test files use consistent 4-space indentation.
        
        Checks each non-empty, non-comment line in the provided test files and asserts that any leading spaces are a multiple of four. Raises an assertion error identifying the file and line number when an inconsistency is found.
        
        Parameters:
            jekyll_test_file (Path): Path to tests/workflows/test_jekyll_workflow.py.
            static_test_file (Path): Path to tests/workflows/test_static_workflow.py.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    if line.strip() and not line.strip().startswith('#'):
                        leading = len(line) - len(line.lstrip(' '))
                        if leading > 0:
                            assert leading % 4 == 0, \
                                f"Line {i} in {test_file.name} has inconsistent indentation"
    
    def test_no_trailing_whitespace(self, jekyll_test_file, static_test_file):
        """
        Ensure workflow test files do not contain excessive trailing whitespace.
        
        Fails if either file contains 5 or more lines that end with whitespace characters; the assertion message lists the first offending line numbers.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                lines = f.readlines()
                
                lines_with_trailing = []
                for i, line in enumerate(lines, 1):
                    if line.rstrip() != line.rstrip('\n\r'):
                        lines_with_trailing.append(i)
                
                # Allow a few lines with trailing whitespace
                assert len(lines_with_trailing) < 5, \
                    f"{test_file.name} has too many lines with trailing whitespace: {lines_with_trailing[:10]}"


class TestTestCoverage:
    """Test that new files have comprehensive coverage"""
    
    def test_jekyll_covers_jekyll_specific_features(self, jekyll_test_file):
        """
        Verify the Jekyll workflow test file references Jekyll-specific features.
        
        Checks that the provided test file contains at least two of the canonical Jekyll indicators: 'jekyll-build-pages', 'Build with Jekyll', or '_site'.
        
        Parameters:
            jekyll_test_file (Path): Path to the Jekyll workflow test file to inspect.
        """
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            
            jekyll_features = ['jekyll-build-pages', 'Build with Jekyll', '_site']
            covered = sum(1 for feature in jekyll_features if feature in content)
            
            assert covered >= 2, \
                "Jekyll test should cover Jekyll-specific features"
    
    def test_static_covers_static_specific_features(self, static_test_file):
        """
        Verify the static workflow test file asserts static-specific features for full-repository uploads.
        
        Asserts that the file content contains the token 'path' and either a '.' character or the word 'entire' (case-insensitive), indicating the test covers uploading the entire repository.
        """
        with open(static_test_file, 'r') as f:
            content = f.read()
            
            # Static workflow uploads entire repo
            assert 'path' in content and ('.' in content or 'entire' in content.lower()), \
                "Static test should cover static-specific features (full repo upload)"
    
    def test_both_cover_github_pages_deployment(self, jekyll_test_file, static_test_file):
        """
        Assert that each provided workflow test file references GitHub Pages deployment.
        
        Checks that the file content contains the words "pages" and "deploy" (case-insensitive); raises an AssertionError naming the file if either term is missing.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'pages' in content.lower() and 'deploy' in content.lower(), \
                    f"{test_file.name} should cover Pages deployment"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])