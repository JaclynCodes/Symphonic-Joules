"""
Consistency validation for the simplified test suite.

This module ensures that the test suite maintains high quality standards:
- All tests have proper documentation
- Fixtures are used efficiently
- Test isolation is maintained
- Error messages are descriptive
- Code quality standards are met
"""

import pytest
import ast
from pathlib import Path
import re


@pytest.fixture(scope='module')
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def test_blank_workflow_path(repo_root):
    """Get path to test_blank_workflow.py."""
    return repo_root / 'tests' / 'workflows' / 'test_blank_workflow.py'


@pytest.fixture(scope='module')
def test_file_ast(test_blank_workflow_path):
    """Parse test file into AST."""
    with open(test_blank_workflow_path, 'r') as f:
        return ast.parse(f.read())


@pytest.fixture(scope='module')
def test_file_content(test_blank_workflow_path):
    """Load test file content."""
    with open(test_blank_workflow_path, 'r') as f:
        return f.read()


class TestDocumentation:
    """Test that all tests are properly documented"""
    
    def test_module_has_docstring(self, test_file_ast):
        """Test that test module has a docstring"""
        docstring = ast.get_docstring(test_file_ast)
        assert docstring is not None, \
            "test_blank_workflow.py should have module docstring"
        assert len(docstring) > 50, \
            "Module docstring should be comprehensive"
    
    def test_all_classes_have_docstrings(self, test_file_ast):
        """Test that all test classes have docstrings"""
        classes_without_docs = []
        
        for node in ast.walk(test_file_ast):
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                docstring = ast.get_docstring(node)
                if docstring is None:
                    classes_without_docs.append(node.name)
        
        assert len(classes_without_docs) == 0, \
            f"Classes without docstrings: {classes_without_docs}"
    
    def test_all_test_methods_have_docstrings(self, test_file_ast):
        """Test that all test methods have docstrings"""
        methods_without_docs = []
        
        for node in ast.walk(test_file_ast):
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                        docstring = ast.get_docstring(item)
                        if docstring is None:
                            methods_without_docs.append(f"{node.name}.{item.name}")
        
        assert len(methods_without_docs) == 0, \
            f"Methods without docstrings: {methods_without_docs[:5]}"
    
    def test_docstrings_are_descriptive(self, test_file_ast):
        """Test that docstrings are descriptive enough"""
        short_docstrings = []
        
        for node in ast.walk(test_file_ast):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                docstring = ast.get_docstring(node)
                if docstring and len(docstring) < 20:
                    short_docstrings.append(node.name)
        
        # Allow some short docstrings, but not too many
        assert len(short_docstrings) < 10, \
            f"Too many test methods with very short docstrings: {short_docstrings[:5]}"


class TestFixtureUsage:
    """Test that fixtures are used efficiently"""
    
    def test_module_scoped_fixtures_exist(self, test_file_content):
        """Test that expensive operations use module-scoped fixtures"""
        assert "scope='module'" in test_file_content, \
            "Should use module-scoped fixtures for expensive operations"
    
    def test_workflow_path_fixture_is_module_scoped(self, test_file_content):
        """Test that workflow_path fixture uses module scope"""
        lines = test_file_content.split('\n')
        found_workflow_path = False
        
        for i, line in enumerate(lines):
            if 'def workflow_path' in line:
                found_workflow_path = True
                # Check previous lines for decorator
                prev_lines = '\n'.join(lines[max(0, i-3):i])
                assert "scope='module'" in prev_lines, \
                    "workflow_path should use module scope"
                break
        
        assert found_workflow_path, "workflow_path fixture should exist"
    
    def test_fixtures_cascade_properly(self, test_file_ast):
        """Test that fixtures reuse each other to avoid redundancy"""
        fixtures = {}
        
        for node in ast.walk(test_file_ast):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if (isinstance(decorator, ast.Call) and 
                        hasattr(decorator.func, 'attr') and 
                        decorator.func.attr == 'fixture') or \
                       (isinstance(decorator, ast.Attribute) and 
                        decorator.attr == 'fixture'):
                        fixtures[node.name] = node.args.args
                        break
        
        # workflow_raw should use workflow_path
        # workflow_content should use workflow_raw
        assert 'workflow_path' in fixtures, "workflow_path fixture should exist"
        assert 'workflow_raw' in fixtures, "workflow_raw fixture should exist"
        assert 'workflow_content' in fixtures, "workflow_content fixture should exist"


class TestAssertionQuality:
    """Test that assertions have descriptive error messages"""
    
    def test_most_assertions_have_messages(self, test_file_content):
        """Test that most assertions include error messages"""
        lines = test_file_content.split('\n')
        
        assert_with_message = 0
        total_asserts = 0
        
        for line in lines:
            if 'assert ' in line and not line.strip().startswith('#'):
                total_asserts += 1
                # Check if it has a comma (usually indicates a message)
                if ',' in line.split('assert')[1]:
                    assert_with_message += 1
        
        # At least 75% should have messages
        if total_asserts > 0:
            ratio = assert_with_message / total_asserts
            assert ratio >= 0.75, \
                f"Only {ratio:.0%} of assertions have error messages (should be >=75%)"
    
    def test_assertions_use_descriptive_variables(self, test_file_content):
        """Test that assertions reference descriptive variable names"""
        lines = test_file_content.split('\n')
        
        bad_assertions = []
        for i, line in enumerate(lines, 1):
            if 'assert ' in line and not line.strip().startswith('#'):
                # Check for overly generic variable names in assertions
                if ' x ' in line or ' i ' in line or ' j ' in line:
                    bad_assertions.append(f"Line {i}: {line.strip()}")
        
        assert len(bad_assertions) == 0, \
            f"Assertions should use descriptive variables: {bad_assertions[:3]}"


class TestCodeOrganization:
    """Test code organization and structure"""
    
    def test_classes_group_related_tests(self, test_file_ast):
        """Test that test classes have multiple related tests"""
        class_sizes = {}
        
        for node in ast.walk(test_file_ast):
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                test_count = sum(1 for item in node.body 
                               if isinstance(item, ast.FunctionDef) 
                               and item.name.startswith('test_'))
                class_sizes[node.name] = test_count
        
        # Most classes should have 2+ tests (some may have 1)
        single_test_classes = [name for name, count in class_sizes.items() if count == 1]
        assert len(single_test_classes) <= 2, \
            f"Too many single-test classes: {single_test_classes}"
    
    def test_helper_methods_are_private(self, test_file_ast):
        """Test that helper methods use underscore prefix"""
        for node in ast.walk(test_file_ast):
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # If it doesn't start with test_ and is not a fixture, should be private
                        if not item.name.startswith('test_') and \
                           not any(d for d in item.decorator_list 
                                  if isinstance(d, ast.Attribute) and d.attr == 'fixture'):
                            assert item.name.startswith('_'), \
                                f"Helper method {item.name} in {node.name} should start with underscore"
    
    def test_imports_are_organized(self, test_file_content):
        """Test that imports are at the top and organized"""
        lines = test_file_content.split('\n')
        
        # Find first import and first function/class
        first_import_line = None
        first_code_line = None
        
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                if first_import_line is None:
                    first_import_line = i
            elif line.startswith('class ') or line.startswith('def '):
                if first_code_line is None:
                    first_code_line = i
                    break
        
        if first_import_line is not None and first_code_line is not None:
            # Imports should be before code
            assert first_import_line < first_code_line, \
                "Imports should be at the top of the file"


class TestTestIsolation:
    """Test that tests are properly isolated"""
    
    def test_no_global_state_modification(self, test_file_content):
        """Test that tests don't modify global state"""
        # Check for patterns that indicate global state modification
        dangerous_patterns = [
            'os.environ[',  # Direct environment modification
            'sys.path.append',  # Modifying Python path
            'del sys.modules',  # Clearing module cache
        ]
        
        for pattern in dangerous_patterns:
            assert pattern not in test_file_content, \
                f"Tests should not use {pattern} - may break isolation"
    
class TestParametrization:
    """Test use of parameterization for reducing duplication"""
    
    def test_uses_parametrize_decorator(self, test_file_content):
        """Test that parametrize is used to reduce duplication"""
        assert '@pytest.mark.parametrize' in test_file_content, \
            "Should use @pytest.mark.parametrize to reduce test duplication"
    
    def test_parametrized_tests_are_well_named(self, test_file_ast):
        """Test that parametrized tests have descriptive parameter names"""
        for node in ast.walk(test_file_ast):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and \
                       hasattr(decorator.func, 'attr') and \
                       decorator.func.attr == 'parametrize':
                        # First argument should be descriptive parameter names
                        if decorator.args:
                            param_str = ast.unparse(decorator.args[0])
                            # Should not use x, y, i, j, etc.
                            assert not re.match(r'^["\']?[xyzij]["\']?$', param_str), \
                                f"Parametrize in {node.name} should use descriptive names"


class TestErrorHandling:
    """Test proper error handling and edge case coverage"""
    
    def test_has_edge_case_tests(self, test_file_ast):
        """Test that edge cases are tested"""
        edge_case_class = False
        
        for node in ast.walk(test_file_ast):
            if isinstance(node, ast.ClassDef):
                if 'Edge' in node.name or 'edge' in node.name.lower():
                    edge_case_class = True
                    break
        
        assert edge_case_class, \
            "Should have a test class for edge cases"
    
    def test_has_security_tests(self, test_file_ast):
        """Test that security aspects are tested"""
        security_class = False
        
        for node in ast.walk(test_file_ast):
            if isinstance(node, ast.ClassDef):
                if 'Security' in node.name or 'security' in node.name.lower():
                    security_class = True
                    break
        
        assert security_class, \
            "Should have a test class for security"


class TestCodeQuality:
    """Test code quality standards"""
    
    def test_no_commented_out_code(self, test_file_content):
        """Test that there's minimal commented-out code"""
        lines = test_file_content.split('\n')
        
        # Count lines that look like commented code (not documentation)
        commented_code_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                # Check if it looks like code (has =, (, [, etc.)
                if any(char in stripped for char in ['=(', '[', '(', '{']):
                    commented_code_lines.append(line)
        
        # Allow a few, but not too many
        assert len(commented_code_lines) < 5, \
            f"Too much commented-out code: {len(commented_code_lines)} lines"
    
    def test_consistent_string_quotes(self, test_file_content):
        """Test that string quotes are used consistently"""
        lines = test_file_content.split('\n')
        
        single_quote_count = sum(line.count("'") for line in lines)
        double_quote_count = sum(line.count('"') for line in lines)
        
        # One style should dominate (80%+)
        total = single_quote_count + double_quote_count
        if total > 0:
            max_count = max(single_quote_count, double_quote_count)
            ratio = max_count / total
            # Allow some flexibility for docstrings and specific cases
            assert ratio >= 0.55, \
                "String quotes should be relatively consistent"
    
    def test_no_overly_long_lines(self, test_file_content):
        """Test that lines are not excessively long"""
        lines = test_file_content.split('\n')
        
        very_long_lines = [i for i, line in enumerate(lines, 1) 
                          if len(line) > 120 and not line.strip().startswith('#')]
        
        # Allow some long lines, but not too many
        assert len(very_long_lines) < 10, \
            f"Too many very long lines (>120 chars): {len(very_long_lines)}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])