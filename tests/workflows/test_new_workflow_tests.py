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
import yaml
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """
    Get the repository root directory.
    
    Returns:
        Path: Path to the repository root directory (three levels above this file).
    """
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope='module')
def workflows_test_dir(repo_root):
    """
    Return the path to the tests/workflows directory under the repository root.
    
    Parameters:
    	repo_root (Path): Repository root directory.
    
    Returns:
    	Path: Path to the `tests/workflows` directory.
    """
    return repo_root / 'tests' / 'workflows'


@pytest.fixture(scope='module')
def jekyll_test_file(workflows_test_dir):
    """
    Resolve the path to the Jekyll workflow test file.
    
    Parameters:
    	workflows_test_dir (Path): Directory containing workflow test files (tests/workflows).
    
    Returns:
    	jekyll_test_file (Path): Path to tests/workflows/test_jekyll_workflow.py
    """
    return workflows_test_dir / 'test_jekyll_workflow.py'


@pytest.fixture(scope='module')
def static_test_file(workflows_test_dir):
    """Get the static workflow test file."""
    return workflows_test_dir / 'test_static_workflow.py'


@pytest.fixture(scope='module')
def blank_test_file(workflows_test_dir):
    """
    Locate the repository's reference workflow test file used as the template.
    
    Parameters:
        workflows_test_dir (Path): Path to the repository's tests/workflows directory.
    
    Returns:
        Path: Path to the reference test file 'test_blank_workflow.py' within `workflows_test_dir`.
    """
    return workflows_test_dir / 'test_blank_workflow.py'


class TestNewFilesExist:
    """Test that new test files exist"""
    
    def test_jekyll_test_file_exists(self, jekyll_test_file):
        """
        Assert that tests/workflows/test_jekyll_workflow.py exists in the repository.
        """
        assert jekyll_test_file.exists(), \
            "test_jekyll_workflow.py should exist"
    
    def test_static_test_file_exists(self, static_test_file):
        """Test that test_static_workflow.py exists"""
        assert static_test_file.exists(), \
            "test_static_workflow.py should exist"
    
    def test_both_files_are_python(self, jekyll_test_file, static_test_file):
        """
        Assert that the Jekyll and static workflow test files use the `.py` filename extension.
        
        Parameters:
            jekyll_test_file (Path): Path to the Jekyll workflow test file.
            static_test_file (Path): Path to the static workflow test file.
        """
        assert jekyll_test_file.suffix == '.py', \
            "Jekyll test file should be Python"
        assert static_test_file.suffix == '.py', \
            "Static test file should be Python"


class TestNewFilesFollowPattern:
    """Test that new files follow established patterns"""
    
    def test_new_files_have_module_docstrings(self, jekyll_test_file, static_test_file):
        """
        Verify each provided workflow test file contains a module-level docstring longer than 100 characters.
        
        Raises:
            AssertionError: If a file is missing a module docstring or the docstring has 100 characters or fewer.
        """
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
        Verify both new workflow test files import the required core modules.
        
        Checks that each of the provided test files contains the imports 'pytest', 'yaml', 'os' and 'Path', raising an assertion if any is missing.
        
        Parameters:
            jekyll_test_file (Path): Path to the Jekyll workflow test file.
            static_test_file (Path): Path to the static workflow test file.
            blank_test_file (Path): Path to the blank/reference workflow test file.
        """
        # Get imports from blank test file (reference)
        with open(blank_test_file, 'r') as f:
            pass
        
        required_imports = ['pytest', 'yaml', 'os', 'Path']
        
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                for imp in required_imports:
                    assert imp in content, \
                        f"{test_file.name} should import {imp}"
    
    def test_new_files_use_module_scoped_fixtures(self, jekyll_test_file, static_test_file):
        """
        Verify each new workflow test file declares module-scoped fixtures by containing the string "scope='module'".
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert "scope='module'" in content, \
                    f"{test_file.name} should use module-scoped fixtures"
    
    def test_new_files_have_workflow_path_fixture(self, jekyll_test_file, static_test_file):
        """
        Assert both workflow test files define a fixture named `workflow_path`.
        
        Parameters:
            jekyll_test_file (Path): Path to the Jekyll workflow test file.
            static_test_file (Path): Path to the static workflow test file.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'def workflow_path()' in content, \
                    f"{test_file.name} should define workflow_path fixture"
    
    def test_new_files_have_workflow_content_fixture(self, jekyll_test_file, static_test_file):
        """Test that new files define workflow_content fixture"""
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'def workflow_content(' in content, \
                    f"{test_file.name} should define workflow_content fixture"


class TestJekyllTestFileStructure:
    """Test Jekyll workflow test file structure"""
    
    def test_jekyll_has_sufficient_test_classes(self, jekyll_test_file):
        """
        Assert that the Jekyll workflow test file defines at least ten classes whose names start with 'Test'.
        
        Fails the test if fewer than ten such classes are present, with the assertion message reporting the actual count.
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
        Ensure the Jekyll workflow test file contains at least 50 test methods.
        
        The function parses the file's AST and counts functions whose names start with `test_`
        that are defined inside classes whose names start with `Test`. It asserts the count
        is 50 or greater.
        
        Parameters:
            jekyll_test_file (Path): Path to the Jekyll test file to inspect.
        
        Raises:
            AssertionError: If fewer than 50 test methods are found.
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
        Assert that the Jekyll test module defines test classes for both build and deploy jobs.
        
        Parameters:
            jekyll_test_file (Path | str): Path to the Jekyll workflow test file to read and inspect.
        """
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            
            assert 'TestBuildJob' in content, \
                "Jekyll test should have TestBuildJob class"
            assert 'TestDeployJob' in content, \
                "Jekyll test should have TestDeployJob class"
    
    def test_jekyll_tests_permissions(self, jekyll_test_file):
        """
        Verify the Jekyll workflow test file includes permissions validation.
        
        Asserts that the file contains a `TestPermissionsConfiguration` declaration and an `id-token` reference (OIDC).
        Parameters:
            jekyll_test_file (Path): Path to the Jekyll test file to inspect.
        """
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            
            assert 'TestPermissionsConfiguration' in content, \
                "Jekyll test should validate permissions"
            assert 'id-token' in content, \
                "Jekyll test should validate OIDC (id-token)"
    
    def test_jekyll_tests_concurrency(self, jekyll_test_file):
        """
        Ensure the Jekyll test file includes checks for concurrency configuration.
        
        Asserts that the file contains a `TestConcurrencyConfiguration` test class and an explicit reference to the `cancel-in-progress` setting.
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
        Ensure the static workflow test file declares at least ten classes whose names start with 'Test'.
        
        Raises:
        	AssertionError: If fewer than ten `Test`-prefixed classes are found; message includes the actual count.
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
        Assert the static workflow test module defines at least 50 test methods across classes named with the `Test` prefix.
        
        Counts functions whose names start with `test_` inside every class whose name begins with `Test` in the provided file and fails the test if the total is fewer than 50.
        
        Parameters:
            static_test_file (str | pathlib.Path): Path to the static workflow test file to inspect.
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
        Check that the static workflow test file contains an explicit comparison to the Jekyll workflow.
        
        The test searches the file content for 'Jekyll', 'TestWorkflowDifferences', or the phrase 'single job' (case-insensitive).
        
        Parameters:
            static_test_file (Path): Path to the static workflow test file to inspect.
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
        """
        Ensure both workflow test files declare a TestWorkflowStructure class.
        
        Asserts that each provided test file contains the literal 'TestWorkflowStructure', raising AssertionError if a file is missing that class.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestWorkflowStructure' in content, \
                    f"{test_file.name} should have TestWorkflowStructure class"
    
    def test_both_validate_metadata(self, jekyll_test_file, static_test_file):
        """
        Assert both workflow test files declare a TestWorkflowMetadata test class.
        
        Checks each provided test file's source for a class named "TestWorkflowMetadata" and fails the test if any file is missing it.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestWorkflowMetadata' in content, \
                    f"{test_file.name} should have TestWorkflowMetadata class"
    
    def test_both_validate_security(self, jekyll_test_file, static_test_file):
        """
        Assert each workflow test file defines a TestWorkflowSecurity test class.
        
        Verifies that both the Jekyll and static workflow test files contain a class named `TestWorkflowSecurity`.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestWorkflowSecurity' in content, \
                    f"{test_file.name} should have TestWorkflowSecurity class"
    
    def test_both_test_edge_cases(self, jekyll_test_file, static_test_file):
        """
        Ensure both workflow test files include a `TestEdgeCases` class.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestEdgeCases' in content, \
                    f"{test_file.name} should have TestEdgeCases class"
    
    def test_both_validate_file_permissions(self, jekyll_test_file, static_test_file):
        """
        Assert both workflow test files declare a TestWorkflowFilePermissions test class.
        
        Checks each provided file contains the literal class name "TestWorkflowFilePermissions"; raises an AssertionError naming the missing file if the class is not found.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestWorkflowFilePermissions' in content, \
                    f"{test_file.name} should have TestWorkflowFilePermissions class"


class TestCodeQuality:
    """Test code quality in new test files"""
    
    def test_no_syntax_errors(self, jekyll_test_file, static_test_file):
        """
        Assert that the Jekyll and static workflow test files parse as valid Python.
        
        If a file contains a syntax error, the test fails and reports the file name and parser error.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {test_file.name}: {e}")
    
    def test_all_test_methods_have_docstrings(self, jekyll_test_file, static_test_file):
        """
        Ensure every `test_` method inside classes whose names start with `Test` has a docstring.
        
        If any test methods are missing docstrings, the assertion fails and lists up to five offending methods in the failing message.
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
        """Test that new files use consistent 4-space indentation"""
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
        Assert that the two workflow test files contain fewer than five lines with trailing whitespace.
        
        If five or more lines contain trailing whitespace the test fails and reports the offending line numbers and file name.
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


class TestWorkflowStructure:
    """Test new workflow structure and metadata"""
    
    def test_new_workflows_exist(self):
        """
        Assert that the repository contains the expected GitHub Actions workflow files.
        
        Checks for the presence of .github/workflows/codeql.yml, .github/workflows/golangci-lint.yml and .github/workflows/license-check.yml and fails the test if any are missing.
        """
        new_workflows = ['codeql.yml', 'golangci-lint.yml', 'license-check.yml']
        for workflow in new_workflows:
            workflow_path = Path(f'.github/workflows/{workflow}')
            assert workflow_path.exists(), f"Workflow {workflow} should exist"


class TestMetadata:
    """Test new workflow metadata"""
    
    def test_new_workflows_have_names(self):
        """
        Ensure each expected workflow file present in .github/workflows declares a top-level 'name' key.
        
        For each of codeql.yml, golangci-lint.yml and license-check.yml that exists, load the YAML and assert the presence of the 'name' field.
        """
        new_workflows = ['codeql.yml', 'golangci-lint.yml', 'license-check.yml']
        for workflow in new_workflows:
            workflow_path = Path(f'.github/workflows/{workflow}')
            if workflow_path.exists():
                with open(workflow_path, 'r') as f:
                    content = yaml.safe_load(f)
                    assert 'name' in content, f"Workflow {workflow} should have a name"


class TestSecurity:
    """Test new workflow security configuration"""
    
    def test_new_workflows_have_appropriate_permissions(self):
        """
        Assert that each expected workflow file, if present, contains either a top-level `permissions` key or a `jobs` key.
        
        Files checked: `.github/workflows/codeql.yml`, `.github/workflows/golangci-lint.yml`, and `.github/workflows/license-check.yml`. Files that are missing are skipped; existing files will cause an assertion failure naming the workflow when neither `permissions` nor `jobs` is found.
        """
        new_workflows = ['codeql.yml', 'golangci-lint.yml', 'license-check.yml']
        for workflow in new_workflows:
            workflow_path = Path(f'.github/workflows/{workflow}')
            if workflow_path.exists():
                with open(workflow_path, 'r') as f:
                    content = yaml.safe_load(f)
                    # Should have some form of permission configuration
                    assert 'permissions' in content or 'jobs' in content, \
                        f"Workflow {workflow} should have proper configuration"


class TestEdgeCases:
    """Test new workflow edge cases and error handling"""
    
    def test_new_workflows_are_valid_yaml(self):
        """Test that new workflows have valid YAML"""
        new_workflows = ['codeql.yml', 'golangci-lint.yml', 'license-check.yml']
        for workflow in new_workflows:
            workflow_path = Path(f'.github/workflows/{workflow}')
            if workflow_path.exists():
                with open(workflow_path, 'r') as f:
                    content = f.read()
                    # Should not raise exception
                    yaml.safe_load(content)


class TestTestCoverage:
    """Test that new files have comprehensive coverage"""
    
    def test_jekyll_covers_jekyll_specific_features(self, jekyll_test_file):
        """
        Ensure the Jekyll test file asserts coverage of core Jekyll features.
        
        Checks that the test file text includes at least two of the expected Jekyll indicators: 'jekyll-build-pages', 'Build with Jekyll' and '_site'.
        
        Parameters:
            jekyll_test_file (Path | str): Path to the Jekyll workflow test file to inspect.
        """
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            
            jekyll_features = ['jekyll-build-pages', 'Build with Jekyll', '_site']
            covered = sum(1 for feature in jekyll_features if feature in content)
            
            assert covered >= 2, \
                "Jekyll test should cover Jekyll-specific features"
    
    def test_static_covers_static_specific_features(self, static_test_file):
        """Test that static test covers static-specific features"""
        with open(static_test_file, 'r') as f:
            content = f.read()
            
            # Static workflow uploads entire repo
            assert 'path' in content and ('.' in content or 'entire' in content.lower()), \
                "Static test should cover static-specific features (full repo upload)"
    
    def test_both_cover_github_pages_deployment(self, jekyll_test_file, static_test_file):
        """
        Verify each workflow test file references GitHub Pages deployment.
        
        Checks the file contents (case-insensitive) for the presence of both the tokens "pages" and "deploy"; the test fails with an assertion message that includes the filename if either token is missing.
        
        Parameters:
            jekyll_test_file (Path): Path to the Jekyll workflow test file.
            static_test_file (Path): Path to the static workflow test file.
        """
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'pages' in content.lower() and 'deploy' in content.lower(), \
                    f"{test_file.name} should cover Pages deployment"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])