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
        root (Path): Path to the repository root directory (two levels up from this file).
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def readme_path(repo_root):
    """
    Return the path to the tests/README.md file within the repository.
    
    Parameters:
    	repo_root (Path): Repository root directory.
    
    Returns:
    	Path: Path to tests/README.md relative to `repo_root`.
    """
    return repo_root / 'tests' / 'README.md'


@pytest.fixture(scope='module')
def readme_content(readme_path):
    """
    Return the contents of the README file at the given path.
    
    Parameters:
        readme_path (str | pathlib.Path): Path to the README.md file.
    
    Returns:
        str: Contents of the README file.
    """
    with open(readme_path, 'r') as f:
        return f.read()


class TestREADMEStructure:
    """Test README structure and completeness"""
    
    def test_readme_exists(self, readme_path):
        """Test that tests/README.md exists"""
        assert readme_path.exists(), "tests/README.md must exist"
    
    def test_readme_not_empty(self, readme_content):
        """Test that README has substantial content"""
        assert len(readme_content) > 1000, \
            "README should be comprehensive (> 1000 characters)"
    
    def test_readme_has_overview(self, readme_content):
        """
        Check that the README contains an Overview section.
        
        Asserts that the README content includes either '# Overview' or '## Overview'.
        """
        assert '## Overview' in readme_content or '# Overview' in readme_content, \
            "README should have an overview section"
    
    def test_readme_has_structure_section(self, readme_content):
        """Test that README documents test structure"""
        assert '## Test Structure' in readme_content or \
               '## Structure' in readme_content, \
            "README should document test structure"
    
    def test_readme_has_running_instructions(self, readme_content):
        """Test that README includes instructions for running tests"""
        assert '## Running Tests' in readme_content or \
               '## Running' in readme_content, \
            "README should have running tests section"


class TestREADMETestCounts:
    """Test that README accurately reflects test counts"""
    
    def test_readme_documents_total_test_count(self, readme_content, repo_root):
        """
        Verify the README documents the repository's total test count and that the documented number matches the actual count within a small tolerance.
        
        This test counts actual tests by parsing Python files under tests/workflows: it tallies methods whose names start with `test_` inside classes whose names start with `Test`. It then extracts numeric occurrences of the form "N tests" from the README and asserts that the actual total is either listed exactly or is within 5 of any documented count.
        
        Parameters:
            readme_content (str): Contents of tests/README.md.
            repo_root (pathlib.Path): Path to the repository root.
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
        Assert the README mentions the blank workflow test.
        
        Parameters:
            readme_content (str): Contents of tests/README.md to search for references to the blank workflow.
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
        """Test that README documents static workflow test count"""
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
        """Test that README uses python -m pytest syntax"""
        assert 'python' in readme_content.lower() and '-m pytest' in readme_content, \
            "README should show 'python -m pytest' syntax"
    
    def test_readme_shows_verbose_flag(self, readme_content):
        """
        Verify the README demonstrates pytest's verbose output flag.
        
        Checks that the README contains either '-v' or '--verbose' to illustrate running tests with increased verbosity.
        """
        assert '-v' in readme_content or '--verbose' in readme_content, \
            "README should demonstrate verbose output"
    
    def test_readme_shows_specific_file_execution(self, readme_content):
        """
        Checks that the README documents how to run specific test files.
        
        Asserts the README contains a reference to a test-file pattern (e.g. `tests/workflows/test_*.py`) or a specific test file name such as `test_blank_workflow.py`.
        """
        # Should show pattern like: pytest tests/workflows/test_*.py
        assert 'tests/workflows/test_' in readme_content or \
               'test_blank_workflow.py' in readme_content, \
            "README should show how to run specific test files"
    
    def test_readme_shows_specific_class_execution(self, readme_content):
        """
        Verify the README demonstrates how to run a specific test class.
        
        Checks that the README contains either the pytest class-selector syntax (a `::` pattern)
        or a case-insensitive mention of "test class".
        
        Parameters:
            readme_content (str): Contents of tests/README.md.
        """
        # Should show pattern like: pytest file.py::TestClass
        assert '::' in readme_content or 'test class' in readme_content.lower(), \
            "README should show how to run specific test classes"


class TestREADMEDependencies:
    """Test that README accurately documents dependencies"""
    
    def test_readme_mentions_pytest(self, readme_content):
        """Test that README mentions pytest dependency"""
        assert 'pytest' in readme_content.lower(), \
            "README should mention pytest dependency"
    
    def test_readme_mentions_pyyaml(self, readme_content):
        """
        Verify README mentions PyYAML or YAML.
        """
        assert 'yaml' in readme_content.lower() or 'pyyaml' in readme_content.lower(), \
            "README should mention PyYAML dependency"
    
    def test_readme_mentions_requirements_file(self, readme_content):
        """
        Verify the repository README references requirements.txt.
        
        Parameters:
            readme_content (str): Contents of tests/README.md.
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
        """
        Verify the README documents structure tests.
        """
        assert 'structure' in readme_content.lower(), \
            "README should document structure tests"
    
    def test_readme_documents_security_tests(self, readme_content):
        """
        Check that the README documents security tests.
        
        Parameters:
            readme_content (str): The full text of tests/README.md to search for the term "security".
        """
        assert 'security' in readme_content.lower(), \
            "README should document security tests"
    
    def test_readme_documents_metadata_tests(self, readme_content):
        """
        Verify the README documents metadata tests.
        """
        assert 'metadata' in readme_content.lower(), \
            "README should document metadata tests"
    
    def test_readme_documents_edge_case_tests(self, readme_content):
        """Test that README mentions edge case tests"""
        assert 'edge' in readme_content.lower(), \
            "README should document edge case tests"


class TestREADMECodeExamples:
    """Test that README code examples are valid"""
    
    def test_readme_bash_blocks_are_valid(self, readme_content):
        """
        Verify that bash/shell code blocks in the README are non-empty and include either `pytest` or `python`.
        
        Parameters:
            readme_content (str): The full contents of tests/README.md to scan for code blocks.
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
        Validate that numeric test-count mentions in the README are internally consistent.
        
        Searches the README content for occurrences of the pattern "N tests" (case-insensitive). If more than one such mention is found, asserts that there are at least two distinct numeric counts to reflect different documented contexts.
        
        Parameters:
            readme_content (str): Full contents of tests/README.md to be searched for test-count mentions.
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
        Verify numeric "classes" counts mentioned in the README correspond to the implementation.
        
        Searches the README for occurrences like "X classes". If any are found, parses
        tests/workflows/test_blank_workflow.py and counts class definitions whose names
        start with "Test". Asserts that at least one documented count is within two of
        the actual class count.
        
        Parameters:
            readme_content (str): Contents of tests/README.md.
            repo_root (Path): Path to the repository root used to locate the test file.
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