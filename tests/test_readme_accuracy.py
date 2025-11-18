"""
Tests to validate that tests/README.md accurately documents the test suite.

This module ensures that the README stays in sync with actual test implementation:
- Test counts match documentation
- Test class counts match documentation
- File structure matches documentation
- Run instructions are accurate
- Dependencies are correctly listed
"""

import pytest
import re
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """
    Return the repository root directory.
    
    Returns:
        Path: Path to the repository root (the parent of this file's directory).
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def readme_path(repo_root):
    """
    Return the path to tests/README.md within the repository.
    
    Parameters:
        repo_root (Path): Repository root directory.
    
    Returns:
        Path: Path to the tests/README.md file.
    """
    return repo_root / 'tests' / 'README.md'


@pytest.fixture(scope='module')
def readme_content(readme_path):
    """
    Read and return the contents of the README file at the given path.
    
    Parameters:
        readme_path (Path | str): Path to the README file.
    
    Returns:
        content (str): The README file contents as a string.
    """
    with open(readme_path, 'r') as f:
        return f.read()


class TestREADMEStructure:
    """Test README structure and completeness"""
    
    def test_readme_exists(self, readme_path):
        """Test that tests/README.md exists"""
        assert readme_path.exists(), "tests/README.md must exist"
    
    def test_readme_not_empty(self, readme_content):
        """
        Validate that tests/README.md contains substantial content.
        
        Asserts the README length is greater than 1000 characters.
        """
        assert len(readme_content) > 1000, \
            "README should be comprehensive (> 1000 characters)"
    
    def test_readme_has_overview(self, readme_content):
        """Test that README includes an overview section"""
        assert '## Overview' in readme_content or '# Overview' in readme_content, \
            "README should have an overview section"
    
    def test_readme_has_structure_section(self, readme_content):
        """
        Verify the README documents the repository's test structure.
        
        Asserts that the README contains a "## Test Structure" or "## Structure" section header.
        """
        assert '## Test Structure' in readme_content or \
               '## Structure' in readme_content, \
            "README should document test structure"
    
    def test_readme_has_running_instructions(self, readme_content):
        """
        Verify the README documents how to run the test suite.
        
        Asserts that the README contains a "## Running Tests" or "## Running" section header.
        """
        assert '## Running Tests' in readme_content or \
               '## Running' in readme_content, \
            "README should have running tests section"


class TestREADMETestCounts:
    """Test that README accurately reflects test counts"""
    
    def test_readme_documents_total_test_count(self, readme_content, repo_root):
        """
        Verify that the repository README documents the total number of workflow tests or a close approximation (within 5).
        
        Parameters:
            readme_content (str): Contents of tests/README.md.
            repo_root (pathlib.Path): Path to the repository root used to locate tests/workflows.
        """
        # Extract documented test count
        import ast
        
        # Count actual tests
        test_files = list((repo_root / 'tests' / 'workflows').glob('test_*.py'))
        total_tests = 0
        
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               item.name.startswith('test_'):
                                total_tests += 1
        
        # README should mention the test count somewhere
        # Look for patterns like "43 tests", "72 tests", etc.
        test_count_pattern = r'(\d+)\s+tests?'
        matches = re.findall(test_count_pattern, readme_content, re.IGNORECASE)
        
        if matches:
            documented_counts = [int(m) for m in matches]
            # Total should be documented somewhere
            assert total_tests in documented_counts or \
                   any(abs(total_tests - dc) <= 5 for dc in documented_counts), \
                f"README should document total test count (actual: {total_tests})"
    
    def test_readme_documents_blank_workflow_tests(self, readme_content):
        """
        Assert the README mentions the blank workflow tests.
        
        Checks that the README contains 'test_blank_workflow' or the phrase 'blank workflow' (case-insensitive) and fails if neither is present.
        """
        # Should mention test_blank_workflow.py
        assert 'test_blank_workflow' in readme_content or \
               'blank workflow' in readme_content.lower(), \
            "README should document blank workflow tests"
    
    def test_readme_documents_jekyll_workflow_tests(self, readme_content):
        """Test that README documents Jekyll workflow test count"""
        assert 'test_jekyll_workflow' in readme_content or \
               'jekyll workflow' in readme_content.lower() or \
               'Jekyll workflow' in readme_content, \
            "README should document Jekyll workflow tests"
    
    def test_readme_documents_static_workflow_tests(self, readme_content):
        """
        Check that the README mentions the static workflow tests either by the test name 'test_static_workflow' or by the phrase 'static workflow'.
        """
        assert 'test_static_workflow' in readme_content or \
               'static workflow' in readme_content.lower() or \
               'Static workflow' in readme_content, \
            "README should document static workflow tests"


class TestREADMERunInstructions:
    """Test that README run instructions are accurate"""
    
    def test_readme_shows_pytest_command(self, readme_content):
        """Test that README includes pytest command"""
        assert 'pytest' in readme_content, \
            "README should include pytest command"
    
    def test_readme_shows_python_module_syntax(self, readme_content):
        """
        Check that the README demonstrates running pytest using the "python -m pytest" module syntax.
        
        Asserts the README contains 'python' (case-insensitive) and the literal '-m pytest'.
        """
        assert 'python' in readme_content.lower() and '-m pytest' in readme_content, \
            "README should show 'python -m pytest' syntax"
    
    def test_readme_shows_verbose_flag(self, readme_content):
        """Check that the README demonstrates use of pytest's verbose flag (-v or --verbose)."""
        assert '-v' in readme_content or '--verbose' in readme_content, \
            "README should demonstrate verbose output"
    
    def test_readme_shows_specific_file_execution(self, readme_content):
        """
        Check README demonstrates how to run specific test files, e.g. a path pattern under tests/workflows or an explicit test filename.
        """
        # Should show pattern like: pytest tests/workflows/test_*.py
        assert 'tests/workflows/test_' in readme_content or \
               'test_blank_workflow.py' in readme_content, \
            "README should show how to run specific test files"
    
    def test_readme_shows_specific_class_execution(self, readme_content):
        """
        Check that README demonstrates how to run an individual test class.
        
        Passes if the README contains the pytest class selection syntax (`::`) or a phrase mentioning a test class.
        
        Parameters:
            readme_content (str): The full contents of tests/README.md to inspect.
        """
        # Should show pattern like: pytest file.py::TestClass
        assert '::' in readme_content or 'test class' in readme_content.lower(), \
            "README should show how to run specific test classes"


class TestREADMEDependencies:
    """Test that README accurately documents dependencies"""
    
    def test_readme_mentions_pytest(self, readme_content):
        """
        Check that the repository README mentions pytest.
        """
        assert 'pytest' in readme_content.lower(), \
            "README should mention pytest dependency"
    
    def test_readme_mentions_pyyaml(self, readme_content):
        """Test that README mentions PyYAML dependency"""
        assert 'yaml' in readme_content.lower() or 'pyyaml' in readme_content.lower(), \
            "README should mention PyYAML dependency"
    
    def test_readme_mentions_requirements_file(self, readme_content):
        """
        Check that the repository README mentions requirements.txt.
        """
        assert 'requirements.txt' in readme_content, \
            "README should mention requirements.txt"
    
    def test_readme_shows_install_command(self, readme_content):
        """Test that README shows pip install command"""
        assert 'pip install' in readme_content, \
            "README should show pip install command"


class TestREADMEFileStructure:
    """Test that README accurately reflects file structure"""
    
    def test_readme_lists_test_structure(self, readme_content, repo_root):
        """Test that README lists test file structure"""
        # Check that major test files are mentioned
        test_files = [
            'test_blank_workflow.py',
            'test_jekyll_workflow.py',
            'test_static_workflow.py'
        ]
        
        for test_file in test_files:
            assert test_file in readme_content, \
                f"README should list {test_file}"
    
    def test_readme_mentions_init_files(self, readme_content):
        """Test that README mentions __init__.py files"""
        assert '__init__.py' in readme_content, \
            "README should mention __init__.py files"
    
    def test_readme_mentions_pytest_ini(self, readme_content):
        """Test that README mentions pytest.ini"""
        assert 'pytest.ini' in readme_content, \
            "README should mention pytest.ini configuration"


class TestREADMETestCategories:
    """Test that README documents test categories"""
    
    def test_readme_documents_structure_tests(self, readme_content):
        """Test that README mentions structure validation tests"""
        assert 'structure' in readme_content.lower(), \
            "README should document structure tests"
    
    def test_readme_documents_security_tests(self, readme_content):
        """Test that README mentions security tests"""
        assert 'security' in readme_content.lower(), \
            "README should document security tests"
    
    def test_readme_documents_metadata_tests(self, readme_content):
        """Test that README mentions metadata tests"""
        assert 'metadata' in readme_content.lower(), \
            "README should document metadata tests"
    
    def test_readme_documents_edge_case_tests(self, readme_content):
        """
        Check that the repository README mentions edge case tests.
        """
        assert 'edge' in readme_content.lower(), \
            "README should document edge case tests"


class TestREADMECodeExamples:
    """Test that README code examples are valid"""
    
    def test_readme_bash_blocks_are_valid(self, readme_content):
        """
        Verify that bash/shell code blocks in the README contain non-empty examples and demonstrate pytest or python usage.
        
        Scans the provided README content for fenced code blocks labelled ```bash or ```shell and asserts each block is not empty and includes either "pytest" or "python".
        
        Parameters:
            readme_content (str): The full text of the README to inspect.
        """
        # Extract bash code blocks
        bash_blocks = re.findall(r'```(?:bash|shell)\n(.*?)\n```', 
                                 readme_content, re.DOTALL)
        
        for block in bash_blocks:
            # Basic validation: should have actual commands
            assert len(block.strip()) > 0, \
                "Bash code blocks should not be empty"
            # Should contain pytest or python
            assert 'pytest' in block or 'python' in block, \
                "Bash examples should show pytest/python usage"
    
    def test_readme_shows_coverage_command(self, readme_content):
        """Test that README shows how to run tests with coverage"""
        has_coverage = '--cov' in readme_content or 'coverage' in readme_content.lower()
        # This is optional but recommended
        if not has_coverage:
            pytest.skip("Coverage command is optional in README")


class TestREADMEConsistency:
    """Test internal consistency of README"""
    
    def test_readme_test_counts_are_consistent(self, readme_content):
        """
        Verify that numeric "N tests" mentions in the README are internally consistent.
        
        If the README contains more than one "N tests" mention, assert that at least two distinct numeric counts appear. This catches cases where multiple contexts are documented but the same (likely incorrect) count is repeated.
        """
        # Find all mentions of test counts
        test_count_pattern = r'(\d+)\s+tests?'
        matches = re.findall(test_count_pattern, readme_content, re.IGNORECASE)
        
        if len(matches) > 1:
            counts = [int(m) for m in matches]
            # Individual file counts should sum to reasonable total
            # This is a soft check as README might mention different contexts
            assert len(set(counts)) >= 2, \
                "README should mention different test counts for different files"
    
    def test_readme_class_counts_match_implementation(self, readme_content, repo_root):
        """
        Check that any 'N classes' counts mentioned in the README are consistent with the actual test classes in the implementation.
        
        If the README contains one or more patterns like "<n> classes", this test parses tests/workflows/test_blank_workflow.py, counts classes whose names start with "Test", and asserts that at least one documented count is within 2 of the actual class count.
        """
        import ast
        
        # Pattern like "43 tests across 9 test classes"
        class_count_pattern = r'(\d+)\s+(?:test\s+)?classes'
        matches = re.findall(class_count_pattern, readme_content, re.IGNORECASE)
        
        if matches:
            # Count actual test classes in one file as validation
            test_file = repo_root / 'tests' / 'workflows' / 'test_blank_workflow.py'
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                actual_classes = len([node for node in ast.walk(tree)
                                     if isinstance(node, ast.ClassDef)
                                     and node.name.startswith('Test')])
            
            documented_counts = [int(m) for m in matches]
            # At least one documented count should be close to actual
            assert any(abs(actual_classes - dc) <= 2 for dc in documented_counts), \
                f"README class counts should match implementation (actual: {actual_classes})"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])