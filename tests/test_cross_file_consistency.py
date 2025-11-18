"""
Cross-file consistency validation for the test suite.

This module validates consistency across all test files:
- Similar workflows have similar test structures
- Fixture patterns are consistent
- Naming conventions are uniform
- Test organization is parallel across files
- Documentation style is consistent
"""

import pytest
import ast
from pathlib import Path
from typing import List, Dict, Set


@pytest.fixture(scope='module')
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def all_workflow_test_files(repo_root):
    """Get all workflow test files."""
    workflows_dir = repo_root / 'tests' / 'workflows'
    return list(workflows_dir.glob('test_*_workflow.py'))


def extract_test_classes(file_path: Path) -> List[str]:
    """Extract test class names from a file."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    return [node.name for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test')]


def extract_fixtures(file_path: Path) -> List[str]:
    """Extract fixture names from a file."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    fixtures = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and \
                   hasattr(decorator.func, 'attr') and \
                   decorator.func.attr == 'fixture':
                    fixtures.append(node.name)
                    break
                elif isinstance(decorator, ast.Attribute) and \
                     decorator.attr == 'fixture':
                    fixtures.append(node.name)
                    break
    
    return fixtures


class TestConsistentStructure:
    """Test that all workflow test files have consistent structure"""
    
    def test_all_files_have_module_docstring(self, all_workflow_test_files):
        """Test that all test files have module docstrings"""
        for test_file in all_workflow_test_files:
            with open(test_file, 'r') as f:
                tree = ast.parse(f.read())
                docstring = ast.get_docstring(tree)
                
                assert docstring is not None, \
                    f"{test_file.name} should have module docstring"
    
    def test_all_files_have_similar_imports(self, all_workflow_test_files):
        """Test that all files import similar core modules"""
        core_imports = ['pytest', 'yaml', 'os', 'Path']
        
        for test_file in all_workflow_test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                
                for imp in core_imports:
                    assert imp in content, \
                        f"{test_file.name} should import {imp}"
    
    def test_all_files_have_workflow_path_fixture(self, all_workflow_test_files):
        """Test that all files define workflow_path fixture"""
        for test_file in all_workflow_test_files:
            fixtures = extract_fixtures(test_file)
            assert 'workflow_path' in fixtures, \
                f"{test_file.name} should define workflow_path fixture"
    
    def test_all_files_have_workflow_content_fixture(self, all_workflow_test_files):
        """Test that all files define workflow_content fixture"""
        for test_file in all_workflow_test_files:
            fixtures = extract_fixtures(test_file)
            assert 'workflow_content' in fixtures, \
                f"{test_file.name} should define workflow_content fixture"


class TestCommonTestClasses:
    """Test that all files include common test class categories"""
    
    def test_all_files_have_structure_tests(self, all_workflow_test_files):
        """Test that all files have TestWorkflowStructure class"""
        for test_file in all_workflow_test_files:
            classes = extract_test_classes(test_file)
            assert 'TestWorkflowStructure' in classes, \
                f"{test_file.name} should have TestWorkflowStructure class"
    
    def test_all_files_have_metadata_tests(self, all_workflow_test_files):
        """Test that all files have TestWorkflowMetadata class"""
        for test_file in all_workflow_test_files:
            classes = extract_test_classes(test_file)
            assert 'TestWorkflowMetadata' in classes, \
                f"{test_file.name} should have TestWorkflowMetadata class"
    
    def test_all_files_have_security_tests(self, all_workflow_test_files):
        """Test that all files have TestWorkflowSecurity class"""
        for test_file in all_workflow_test_files:
            classes = extract_test_classes(test_file)
            assert 'TestWorkflowSecurity' in classes, \
                f"{test_file.name} should have TestWorkflowSecurity class"
    
    def test_all_files_have_edge_case_tests(self, all_workflow_test_files):
        """Test that all files have TestEdgeCases class"""
        for test_file in all_workflow_test_files:
            classes = extract_test_classes(test_file)
            assert 'TestEdgeCases' in classes, \
                f"{test_file.name} should have TestEdgeCases class"


class TestConsistentFixtureUsage:
    """Test that fixtures are used consistently across files"""
    
    def test_workflow_path_fixtures_use_module_scope(self, all_workflow_test_files):
        """Test that workflow_path fixtures use module scope"""
        for test_file in all_workflow_test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                
                # Find workflow_path fixture definition
                if 'def workflow_path()' in content:
                    # Extract the fixture definition
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'def workflow_path()' in line:
                            # Check previous lines for decorator
                            prev_lines = '\n'.join(lines[max(0, i-3):i])
                            assert "scope='module'" in prev_lines, \
                                f"{test_file.name}: workflow_path should use module scope"
                            break
    
    def test_consistent_fixture_naming(self, all_workflow_test_files):
        """Test that fixture naming is consistent across files"""
        common_fixtures = ['workflow_path', 'workflow_raw', 'workflow_content', 'jobs']
        
        fixture_usage = {fixture: [] for fixture in common_fixtures}
        
        for test_file in all_workflow_test_files:
            fixtures = extract_fixtures(test_file)
            for common_fixture in common_fixtures:
                if common_fixture in fixtures:
                    fixture_usage[common_fixture].append(test_file.name)
        
        # At least 2 files should use each common fixture
        for fixture, files in fixture_usage.items():
            assert len(files) >= 2, \
                f"Common fixture '{fixture}' should be used consistently (only in {files})"


class TestConsistentTestNaming:
    """Test that test naming is consistent across files"""
    
    def test_test_methods_start_with_test(self, all_workflow_test_files):
        """Test that all test methods follow test_* naming"""
        for test_file in all_workflow_test_files:
            with open(test_file, 'r') as f:
                tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               not item.name.startswith('_'):
                                assert item.name.startswith('test_'), \
                                    f"{test_file.name}: {item.name} should start with 'test_'"
    
    def test_test_classes_start_with_test(self, all_workflow_test_files):
        """Test that all test classes follow Test* naming"""
        for test_file in all_workflow_test_files:
            classes = extract_test_classes(test_file)
            for cls in classes:
                assert cls.startswith('Test'), \
                    f"{test_file.name}: Class {cls} should start with 'Test'"


class TestConsistentDocumentation:
    """Test that documentation is consistent across files"""
    
    def test_all_test_methods_have_docstrings(self, all_workflow_test_files):
        """Test that all test methods have docstrings"""
        for test_file in all_workflow_test_files:
            with open(test_file, 'r') as f:
                tree = ast.parse(f.read())
                
                methods_without_docs = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               item.name.startswith('test_'):
                                if ast.get_docstring(item) is None:
                                    methods_without_docs.append(f"{node.name}.{item.name}")
                
                assert len(methods_without_docs) == 0, \
                    f"{test_file.name} has methods without docstrings: {methods_without_docs[:3]}"
    
    def test_all_test_classes_have_docstrings(self, all_workflow_test_files):
        """Test that all test classes have docstrings"""
        for test_file in all_workflow_test_files:
            with open(test_file, 'r') as f:
                tree = ast.parse(f.read())
                
                classes_without_docs = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        if ast.get_docstring(node) is None:
                            classes_without_docs.append(node.name)
                
                assert len(classes_without_docs) == 0, \
                    f"{test_file.name} has classes without docstrings: {classes_without_docs}"


class TestSimilarComplexity:
    """Test that files have similar complexity and coverage"""
    
    def test_files_have_similar_test_counts(self, all_workflow_test_files):
        """Test that files have reasonably similar test counts"""
        test_counts = {}
        
        for test_file in all_workflow_test_files:
            with open(test_file, 'r') as f:
                tree = ast.parse(f.read())
                
                count = 0
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and \
                               item.name.startswith('test_'):
                                count += 1
                
                test_counts[test_file.name] = count
        
        # All files should have at least 20 tests
        for file_name, count in test_counts.items():
            assert count >= 20, \
                f"{file_name} should have at least 20 tests (got {count})"
        
        # No file should have more than 3x tests of another (indicates inconsistency)
        min_count = min(test_counts.values())
        max_count = max(test_counts.values())
        assert max_count <= min_count * 3, \
            f"Test count variance too high: {min_count} to {max_count}"
    
    def test_files_have_similar_class_counts(self, all_workflow_test_files):
        """Test that files have reasonably similar test class counts"""
        class_counts = {}
        
        for test_file in all_workflow_test_files:
            classes = extract_test_classes(test_file)
            class_counts[test_file.name] = len(classes)
        
        # All files should have at least 5 test classes
        for file_name, count in class_counts.items():
            assert count >= 5, \
                f"{file_name} should have at least 5 test classes (got {count})"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])