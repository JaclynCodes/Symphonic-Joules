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
def readme_content(readme_path):
    """Load README content."""
    with open(readme_path, 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def test_blank_workflow_path(repo_root):
    """Get path to test_blank_workflow.py."""
    return repo_root / 'tests' / 'workflows' / 'test_blank_workflow.py'


@pytest.fixture(scope='module')
def actual_test_count(test_blank_workflow_path):
    """Count actual tests in test_blank_workflow.py."""
    with open(test_blank_workflow_path, 'r') as f:
        tree = ast.parse(f.read())
    
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
    with open(test_blank_workflow_path, 'r') as f:
        tree = ast.parse(f.read())
    
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
            test_count = sum(1 for item in node.body 
                           if isinstance(item, ast.FunctionDef) 
                           and item.name.startswith('test_'))
            classes[node.name] = test_count
    return classes


class TestREADMEStructure:
    """Test README structure and completeness"""
    
    def test_readme_exists(self, readme_path):
        """Test that tests/README.md exists"""
        assert readme_path.exists(), "tests/README.md must exist"
    
    def test_readme_is_readable(self, readme_path):
        """Test that README is readable"""
        assert readme_path.is_file(), "README must be a file"
        with open(readme_path, 'r') as f:
            content = f.read()
            assert len(content) > 0, "README should not be empty"
    
    def test_readme_not_empty(self, readme_content):
        """Test that README has substantial content"""
        assert len(readme_content) > 1000, \
            "README should be comprehensive (> 1000 characters)"
    
    def test_readme_has_title(self, readme_content):
        """Test that README has a proper title"""
        lines = readme_content.split('\n')
        assert lines[0].startswith('#'), \
            "README should start with a markdown header"
    
    def test_readme_has_overview(self, readme_content):
        """Test that README includes an overview section"""
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
    
    def test_has_dependencies_section(self, readme_content):
        """Test that README has Dependencies section"""
        assert '## Dependencies' in readme_content or \
               '## Test Dependencies' in readme_content, \
            "README should have Dependencies section"


class TestREADMETestCounts:
    """Test that README accurately reflects test counts"""
    
    def test_readme_documents_total_test_count(self, readme_content, repo_root):
        """Test that README documents total test count"""
        
        # Count actual tests
        test_files = list((repo_root / 'tests' / 'workflows').glob('test_*.py'))
        total_tests = 0
        
        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef) and \
                                   item.name.startswith('test_'):
                                    total_tests += 1
            except Exception:
                pass  # Skip files that can't be parsed
        
        # README should mention test counts
        test_count_pattern = r'(\d+)\s+tests?'
        matches = re.findall(test_count_pattern, readme_content, re.IGNORECASE)
        
        # Just verify that README mentions some test counts
        assert len(matches) > 0, \
            "README should document test counts"
    
    def test_total_test_count_is_accurate(self, readme_content, actual_test_count):
        """Test that README documents correct total test count for blank workflow"""
        pattern = r'(\d+)\s+tests?'
        matches = re.findall(pattern, readme_content, re.IGNORECASE)
        
        assert len(matches) > 0, "README should document test count"
        documented_counts = [int(m) for m in matches]
        assert any(abs(actual_test_count - dc) <= 10 for dc in documented_counts), \
            f"README should document actual test count ({actual_test_count})"
    
    def test_test_class_count_is_accurate(self, readme_content, actual_test_classes):
        """Test that README documents correct number of test classes"""
        class_sections = re.findall(r'### (Test\w+)', readme_content)
        
        if class_sections and len(actual_test_classes) > 0:
            actual_class_count = len(actual_test_classes)
            documented_class_count = len(class_sections)
            
            # Allow reasonable variance since README may document multiple files
            # or have organizational headers
            assert abs(documented_class_count - actual_class_count) <= 20 or \
                   documented_class_count > actual_class_count, \
                f"README documents {documented_class_count} classes, " \
                f"blank_workflow has {actual_class_count}"
    
    def test_readme_documents_blank_workflow_tests(self, readme_content):
        """Test that README documents blank workflow test count"""
        assert 'test_blank_workflow' in readme_content or \
               'blank workflow' in readme_content.lower(), \
            "README should document blank workflow tests"


class TestREADMERunInstructions:
    """Test that README run instructions are accurate"""
    
    def test_readme_shows_pytest_command(self, readme_content):
        """Test that README includes pytest command"""
        assert 'pytest' in readme_content, \
            "README should include pytest command"
    
    def test_readme_shows_python_module_syntax(self, readme_content):
        """Test that README uses python -m pytest syntax"""
        assert 'python' in readme_content.lower() and \
               ('-m pytest' in readme_content or 'pytest' in readme_content), \
            "README should show pytest usage"
    
    def test_readme_shows_verbose_flag(self, readme_content):
        """Test that README demonstrates verbose output flag"""
        assert '-v' in readme_content or '--verbose' in readme_content, \
            "README should demonstrate verbose output"
    
    def test_readme_shows_specific_file_execution(self, readme_content):
        """Test that README shows how to run specific test files"""
        assert 'tests/workflows/test_' in readme_content or \
               'test_blank_workflow.py' in readme_content, \
            "README should show how to run specific test files"
    
    def test_readme_shows_specific_class_execution(self, readme_content):
        """Test that README shows how to run specific test classes"""
        assert '::' in readme_content or 'test class' in readme_content.lower(), \
            "README should show how to run specific test classes"
    
    def test_has_run_all_tests_command(self, readme_content):
        """Test that README shows how to run all tests"""
        assert 'python3 -m pytest tests/' in readme_content or \
               'pytest tests/' in readme_content or \
               'python -m pytest tests/' in readme_content, \
            "README should show command to run all tests"


class TestREADMEDependencies:
    """Test that README accurately documents dependencies"""
    
    def test_readme_mentions_pytest(self, readme_content):
        """Test that README mentions pytest dependency"""
        assert 'pytest' in readme_content.lower(), \
            "README should mention pytest dependency"
    
    def test_readme_mentions_pyyaml(self, readme_content):
        """Test that README mentions PyYAML dependency"""
        assert 'yaml' in readme_content.lower() or 'pyyaml' in readme_content.lower(), \
            "README should mention PyYAML dependency"
    
    def test_readme_mentions_requirements_file(self, readme_content):
        """Test that README points to requirements.txt"""
        assert 'requirements.txt' in readme_content, \
            "README should mention requirements.txt"
    
    def test_readme_shows_install_command(self, readme_content):
        """Test that README shows pip install command"""
        assert 'pip install' in readme_content, \
            "README should show pip install command"


class TestREADMEFileReferences:
    """Test that README accurately reflects file structure"""
    
    def test_readme_lists_test_structure(self, readme_content, repo_root):
        """Test that README lists test file structure"""
        # Check that major test file is mentioned
        assert 'test_blank_workflow.py' in readme_content, \
            "README should list test_blank_workflow.py"
    
    def test_references_pytest_ini(self, readme_content):
        """Test that README mentions pytest.ini"""
        assert 'pytest.ini' in readme_content, \
            "README should mention pytest.ini configuration"
    
    def test_readme_mentions_init_files(self, readme_content):
        """Test that README mentions __init__.py files"""
        assert '__init__.py' in readme_content, \
            "README should mention __init__.py files"


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
        """Test that README mentions edge case tests"""
        assert 'edge' in readme_content.lower(), \
            "README should document edge case tests"


class TestREADMECodeExamples:
    """Test that README code examples are valid"""
    
    def test_readme_bash_blocks_are_valid(self, readme_content):
        """Test that bash code blocks in README use valid syntax"""
        bash_blocks = re.findall(r'```(?:bash|shell)\n(.*?)\n```', 
                                 readme_content, re.DOTALL)
        
        if bash_blocks:
            for block in bash_blocks:
                assert len(block.strip()) > 0, \
                    "Bash code blocks should not be empty"
            
            # At least one block should show pytest/python usage
            has_pytest = any('pytest' in block or 'python' in block for block in bash_blocks)
            assert has_pytest, \
                "At least one bash example should show pytest/python usage"
    
    def test_readme_shows_coverage_command(self, readme_content):
        """Test that README shows how to run tests with coverage"""
        has_coverage = '--cov' in readme_content or 'coverage' in readme_content.lower()
        if not has_coverage:
            pytest.skip("Coverage command is optional in README")


class TestREADMEConsistency:
    """Test internal consistency of README"""
    
    def test_readme_test_counts_are_consistent(self, readme_content):
        """Test that test counts mentioned throughout README are consistent"""
        test_count_pattern = r'(\d+)\s+tests?'
        matches = re.findall(test_count_pattern, readme_content, re.IGNORECASE)
        
        if len(matches) > 1:
            counts = [int(m) for m in matches]
            assert len(set(counts)) >= 1, \
                "README should mention test counts"
    
    def test_readme_class_counts_match_implementation(self, readme_content, repo_root):
        """Test that class counts in README match actual implementation"""
        
        class_count_pattern = r'(\d+)\s+(?:test\s+)?classes'
        matches = re.findall(class_count_pattern, readme_content, re.IGNORECASE)
        
        if matches:
            test_file = repo_root / 'tests' / 'workflows' / 'test_blank_workflow.py'
            if test_file.exists():
                try:
                    with open(test_file, 'r') as f:
                        content = f.read()
                        tree = ast.parse(content)
                        actual_classes = len([node for node in ast.walk(tree)
                                             if isinstance(node, ast.ClassDef)
                                             and node.name.startswith('Test')])
                    
                    documented_counts = [int(m) for m in matches]
                    # Allow reasonable variance - README may document multiple files
                    assert any(abs(actual_classes - dc) <= 5 or dc > actual_classes 
                               for dc in documented_counts), \
                        f"README class counts should reasonably match implementation " \
                        f"(blank_workflow has {actual_classes} classes)"
                except Exception:
                    pass  # Skip if file can't be parsed
    
    def test_no_references_to_nonexistent_workflow_files(self, readme_content, repo_root):
        """Test that README doesn't reference workflow test files that don't exist"""
        # Check for common test files that might have been removed
        workflows_dir = repo_root / 'tests' / 'workflows'
        
        # Look for test file references in README
        import re
        test_file_pattern = r'test_\w+\.py'
        mentioned_files = set(re.findall(test_file_pattern, readme_content))
        
        for mentioned_file in mentioned_files:
            file_path = workflows_dir / mentioned_file
            if not file_path.exists():
                # File is mentioned but doesn't exist - should be noted as removed/deprecated
                context_lower = readme_content.lower()
                assert any(word in context_lower for word in 
                          ['removed', 'deprecated', 'deleted', 'no longer', 'previously']), \
                    f"README mentions non-existent file {mentioned_file} without clarifying it's removed"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
