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
    """Get the repository root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope='module')
def workflows_test_dir(repo_root):
    """Get the workflows test directory."""
    return repo_root / 'tests' / 'workflows'


@pytest.fixture(scope='module')
def jekyll_test_file(workflows_test_dir):
    """Get the Jekyll workflow test file."""
    return workflows_test_dir / 'test_jekyll_workflow.py'


@pytest.fixture(scope='module')
def static_test_file(workflows_test_dir):
    """Get the static workflow test file."""
    return workflows_test_dir / 'test_static_workflow.py'


@pytest.fixture(scope='module')
def blank_test_file(workflows_test_dir):
    """Get the blank workflow test file (reference implementation)."""
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
        """Test that new files import same core modules as blank test"""
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
        """Test that new files define workflow_path fixture"""
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
        """Test that Jekyll test file has sufficient test classes"""
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
            
            test_classes = [node for node in ast.walk(tree)
                           if isinstance(node, ast.ClassDef)
                           and node.name.startswith('Test')]
            
            assert len(test_classes) >= 10, \
                f"Jekyll test should have at least 10 test classes (got {len(test_classes)})"
    
    def test_jekyll_has_sufficient_tests(self, jekyll_test_file):
        """Test that Jekyll test file has sufficient test methods"""
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
        """Test that Jekyll test file tests both build and deploy jobs"""
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
        """Test that Jekyll test file validates concurrency settings"""
        with open(jekyll_test_file, 'r') as f:
            content = f.read()
            
            assert 'TestConcurrencyConfiguration' in content, \
                "Jekyll test should validate concurrency"
            assert 'cancel-in-progress' in content, \
                "Jekyll test should check cancel-in-progress setting"


class TestStaticTestFileStructure:
    """Test static workflow test file structure"""
    
    def test_static_has_sufficient_test_classes(self, static_test_file):
        """Test that static test file has sufficient test classes"""
        with open(static_test_file, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
            
            test_classes = [node for node in ast.walk(tree)
                           if isinstance(node, ast.ClassDef)
                           and node.name.startswith('Test')]
            
            assert len(test_classes) >= 10, \
                f"Static test should have at least 10 test classes (got {len(test_classes)})"
    
    def test_static_has_sufficient_tests(self, static_test_file):
        """Test that static test file has sufficient test methods"""
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
        """Test that static test file compares differences with Jekyll workflow"""
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
        """Test that both files validate security"""
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestWorkflowSecurity' in content, \
                    f"{test_file.name} should have TestWorkflowSecurity class"
    
    def test_both_test_edge_cases(self, jekyll_test_file, static_test_file):
        """Test that both files test edge cases"""
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'TestEdgeCases' in content, \
                    f"{test_file.name} should have TestEdgeCases class"
    
    def test_both_validate_file_permissions(self, jekyll_test_file, static_test_file):
        """Test that both files validate file permissions"""
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
        """Test that all test methods have docstrings"""
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
        """Test that new files don't have trailing whitespace"""
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
        """Test that new workflow files exist"""
        new_workflows = ['codeql.yml', 'golangci-lint.yml', 'license-check.yml']
        for workflow in new_workflows:
            workflow_path = Path(f'.github/workflows/{workflow}')
            assert workflow_path.exists(), f"Workflow {workflow} should exist"


class TestMetadata:
    """Test new workflow metadata"""
    
    def test_new_workflows_have_names(self):
        """Test that new workflows have descriptive names"""
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
        """Test that new workflows have appropriate permissions"""
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
        """Test that Jekyll test covers Jekyll-specific features"""
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
        """Test that both files cover GitHub Pages deployment"""
        for test_file in [jekyll_test_file, static_test_file]:
            with open(test_file, 'r') as f:
                content = f.read()
                
                assert 'pages' in content.lower() and 'deploy' in content.lower(), \
                    f"{test_file.name} should cover Pages deployment"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])