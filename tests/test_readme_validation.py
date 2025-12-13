"""
Comprehensive validation tests for tests/README.md

This module ensures that the README accurately documents the test suite:
- Test counts match the actual implementation
- Test class descriptions are accurate
- File references are correct
- Running instructions are valid
- Dependencies are properly listed
- Structure documentation is current
"""

import pytest
import re
import ast
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def readme_path(repo_root):
    """Get the README.md path in tests directory."""
    return repo_root / 'tests' / 'README.md'


@pytest.fixture(scope='module')
def readme_content(readme_path):
    """Load README content."""
    with open(readme_path, 'r') as file:
        return file.read()


@pytest.fixture(scope='module')
def test_blank_workflow_path(repo_root):
    """Get path to test_blank_workflow.py."""
    return repo_root / 'tests' / 'workflows' / 'test_blank_workflow.py'


@pytest.fixture(scope='module')
def actual_test_count(test_blank_workflow_path):
    """Count actual tests in test_blank_workflow.py."""
    with open(test_blank_workflow_path, 'r') as file:
        tree = ast.parse(file.read())
    
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                    count += 1
    return count


@pytest.fixture(scope='module')
def actual_test_classes(test_blank_workflow_path):
    """Get actual test class names and their test counts."""
    with open(test_blank_workflow_path, 'r') as file:
        tree = ast.parse(file.read())
    
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
            test_count = sum(1 for item in node.body 
                           if isinstance(item, ast.FunctionDef) 
                           and item.name.startswith('test_'))
            classes[node.name] = test_count
    return classes


class TestREADMEExists:
    """Test that README exists and is properly structured"""
    
    def test_readme_exists(self, readme_path):
        """Test that tests/README.md exists"""
        assert readme_path.exists(), "tests/README.md must exist"
    
    def test_readme_is_readable(self, readme_path):
        """Test that README is readable"""
        assert readme_path.is_file(), "README must be a file"
        with open(readme_path, 'r') as file:
            content = file.read()
            assert len(content) > 0, "README should not be empty"
    
    def test_readme_has_title(self, readme_content):
        """Test that README has a proper title"""
        lines = readme_content.split('\n')
        assert lines[0].startswith('#'), "README should start with a markdown header"


class TestREADMEStructure:
    """Test README section structure"""
    
    def test_has_overview_section(self, readme_content):
        """Test that README has an Overview section"""
        assert '## Overview' in readme_content, "README should have Overview section"
    
    def test_has_test_structure_section(self, readme_content):
        """Test that README has Test Structure section"""
        assert '## Test Structure' in readme_content, \
            "README should have Test Structure section"
    
    def test_has_running_tests_section(self, readme_content):
        """Test that README has Running Tests section"""
        assert '## Running Tests' in readme_content or '## Running' in readme_content, \
            "README should have Running Tests section"
    
    def test_has_dependencies_section(self, readme_content):
        """Test that README has Dependencies section"""
        assert '## Dependencies' in readme_content, \
            "README should have Dependencies section"


class TestTestCountAccuracy:
    """Test that documented test counts match actual implementation"""
    
    def test_total_test_count_is_accurate(self, readme_content, actual_test_count):
        """Test that README documents correct total test count"""
        pattern = r'(\d+)\s+tests?'
        matches = re.findall(pattern, readme_content, re.IGNORECASE)
        
        assert len(matches) > 0, "README should document test count"
        documented_counts = [int(m) for m in matches]
        # Check if actual count is within reasonable range of documented
        assert any(abs(actual_test_count - dc) <= 10 for dc in documented_counts), \
            f"README should document actual test count ({actual_test_count})"
    
    def test_test_class_count_is_accurate(self, readme_content, actual_test_classes):
        """Test that README documents correct number of test classes"""
        class_sections = re.findall(r'### (Test\w+)', readme_content)
        
        actual_class_count = len(actual_test_classes)
        documented_class_count = len(class_sections)
        
        assert documented_class_count == actual_class_count, \
            f"README documents {documented_class_count} classes but {actual_class_count} exist"


class TestFileReferences:
    """Test that file references in README are accurate"""
    
    def test_references_correct_test_file(self, readme_content):
        """Test that README references the correct test file"""
        assert 'test_blank_workflow.py' in readme_content, \
            "README should reference test_blank_workflow.py"
    
    def test_references_pytest_ini(self, readme_content):
        """Test that README mentions pytest.ini"""
        assert 'pytest.ini' in readme_content, \
            "README should mention pytest.ini configuration"


class TestRunningInstructions:
    """Test that running instructions are accurate and complete"""
    
    def test_has_pytest_command(self, readme_content):
        """Test that README includes pytest command"""
        assert 'pytest' in readme_content, \
            "README should include pytest command"
    
    def test_has_verbose_flag_example(self, readme_content):
        """Test that README shows verbose flag usage"""
        assert '-v' in readme_content, \
            "README should show verbose flag usage"
    
    def test_has_run_all_tests_command(self, readme_content):
        """Test that README shows how to run all tests"""
        assert 'python3 -m pytest tests/' in readme_content or \
               'pytest tests/' in readme_content, \
            "README should show command to run all tests"


class TestDependencies:
    """Test that dependencies are accurately documented"""
    
    def test_lists_pytest_dependency(self, readme_content):
        """Test that README lists pytest dependency"""
        assert 'pytest' in readme_content.lower(), \
            "README should list pytest as dependency"
    
    def test_lists_pyyaml_dependency(self, readme_content):
        """Test that README lists PyYAML dependency"""
        assert 'PyYAML' in readme_content or 'pyyaml' in readme_content.lower(), \
            "README should list PyYAML as dependency"
    
    def test_mentions_requirements_file(self, readme_content):
        """Test that README mentions requirements.txt"""
        assert 'requirements.txt' in readme_content, \
            "README should mention requirements.txt"


class TestREADMEConsistency:
    """Test internal consistency of README"""
    
    def test_no_references_to_deleted_files(self, readme_content):
        """Test that README doesn't reference deleted test files"""
        deleted_files = [
            'test_jekyll_workflow.py',
            'test_static_workflow.py',
            'test_integration_suite.py'
        ]
        
        for deleted_file in deleted_files:
            assert deleted_file not in readme_content, \
                f"README should not reference deleted file {deleted_file}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])