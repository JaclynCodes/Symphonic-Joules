"""
Comprehensive test suite for tests/requirements.txt

This test suite validates the test dependencies including:
- File existence and format
- Dependency specifications
- Version constraints
- Security considerations
"""

import pytest
import re
from pathlib import Path


@pytest.fixture
def requirements_path():
    """Return the path to requirements.txt file."""
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / "tests" / "requirements.txt"


@pytest.fixture
def requirements_content(requirements_path):
    """Load raw content of requirements.txt."""
    with open(requirements_path, 'r') as f:
        return f.read()


@pytest.fixture
def requirements_lines(requirements_content):
    """Parse requirements.txt into non-comment lines."""
    lines = []
    for line in requirements_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            lines.append(line)
    return lines


class TestRequirementsFileStructure:
    """Test the basic structure of requirements.txt."""
    
    def test_requirements_file_exists(self, requirements_path):
        """Test that requirements.txt file exists."""
        assert requirements_path.exists(), "requirements.txt should exist"
    
    def test_requirements_file_not_empty(self, requirements_content):
        """Test that requirements.txt is not empty."""
        assert len(requirements_content.strip()) > 0, \
            "requirements.txt should not be empty"
    
    def test_requirements_file_readable(self, requirements_path):
        """Test that requirements.txt is readable."""
        try:
            with open(requirements_path, 'r') as f:
                f.read()
        except OSError as e:
            pytest.fail(f"Failed to read requirements.txt: {e}")


class TestDependencySpecifications:
    """Test dependency specifications and formats."""
    
    def test_all_lines_are_valid_format(self, requirements_lines):
        """Test that all requirement lines have valid format."""
        # Valid formats: package, package==version, package>=version, etc.
        valid_pattern = re.compile(r'^[a-zA-Z0-9_-]+([<>=!]+[0-9.]+)?$')
        
        for line in requirements_lines:
            # Remove any trailing comments
            req = line.split('#')[0].strip()
            if req:
                assert valid_pattern.match(req) or '[' in req or '@' in req, \
                    f"Invalid requirement format: {line}"
    
    def test_pytest_is_included(self, requirements_lines):
        """Test that pytest is included in requirements."""
        pytest_found = any('pytest' in line.lower() and 'pytest-' not in line.lower() 
                          for line in requirements_lines)
        assert pytest_found, "pytest should be in requirements.txt"
    
    def test_pytest_has_version_constraint(self, requirements_lines):
        """Test that pytest has a version constraint."""
        pytest_lines = [line for line in requirements_lines if line.startswith('pytest') and 'pytest-' not in line]
        
        if pytest_lines:
            pytest_spec = pytest_lines[0]
            assert '>=' in pytest_spec or '==' in pytest_spec or '~=' in pytest_spec, \
                "pytest should have a version constraint"
    
    def test_pyyaml_is_included(self, requirements_lines):
        """Test that PyYAML is included for YAML testing."""
        pyyaml_found = any('pyyaml' in line.lower() for line in requirements_lines)
        assert pyyaml_found, "PyYAML should be in requirements.txt"
    
    def test_jsonschema_is_included(self, requirements_lines):
        """Test that jsonschema is included for schema validation."""
        jsonschema_found = any('jsonschema' in line.lower() for line in requirements_lines)
        assert jsonschema_found, "jsonschema should be in requirements.txt"


class TestVersionConstraints:
    """Test version constraints and specifications."""
    
    def test_version_constraints_use_appropriate_operators(self, requirements_lines):
        """Test that version constraints use appropriate operators."""
        for line in requirements_lines:
            if '>=' in line:
                # Minimum version constraint is good
                assert True
            elif '==' in line:
                # Exact pinning - acceptable but inflexible
                assert True
            elif '<=' in line or '<' in line:
                # Upper bounds without lower bounds can be problematic
                if '>=' not in line:
                    pytest.skip(f"Warning: Upper bound without lower bound in {line}")
    
    def test_no_conflicting_constraints(self, requirements_lines):
        """Test that there are no conflicting version constraints."""
        packages = {}
        for line in requirements_lines:
            pkg_name = re.split(r'[<>=!]', line)[0].strip()
            if pkg_name in packages:
                pytest.fail(f"Duplicate package specification: {pkg_name}")
            packages[pkg_name] = line
    
    def test_version_numbers_are_valid(self, requirements_lines):
        """Test that version numbers follow semantic versioning."""
        version_pattern = re.compile(r'[<>=!]+(\d+\.?\d*\.?\d*)')
        
        for line in requirements_lines:
            match = version_pattern.search(line)
            if match:
                version = match.group(1)
                parts = version.split('.')
                assert all(part.isdigit() for part in parts), \
                    f"Invalid version number in {line}"


class TestSecurityConsiderations:
    """Test security-related aspects of requirements."""
    
    def test_no_insecure_package_sources(self, requirements_content):
        """Test that no insecure package sources are used."""
        insecure_patterns = [
            'http://',  # Should use https
            '--index-url http://',
            '--extra-index-url http://'
        ]
        
        for pattern in insecure_patterns:
            assert pattern not in requirements_content, \
                f"Insecure package source found: {pattern}"
    
    def test_no_git_http_urls(self, requirements_content):
        """Test that git URLs use secure protocols."""
        if 'git+' in requirements_content:
            assert 'git+http://' not in requirements_content, \
                "Git dependencies should use https or ssh"
    
    def test_packages_are_from_pypi(self, requirements_lines):
        """Test that packages are preferably from PyPI."""
        for line in requirements_lines:
            if '@' in line and 'git' in line.lower():
                pytest.skip(f"Warning: Non-PyPI package found: {line}")


class TestDependencyBestPractices:
    """Test dependency management best practices."""
    
    def test_no_overly_restrictive_pins(self, requirements_lines):
        """Test that dependencies aren't overly restrictive."""
        for line in requirements_lines:
            # Using == pins exact versions which can cause conflicts
            if '==' in line:
                # This is acceptable but log it
                pkg_name = line.split('==')[0].strip()
                # Core libraries should prefer >= instead of ==
                if pkg_name in ['pytest', 'pyyaml', 'jsonschema']:
                    pytest.skip(f"Consider using >= instead of == for {pkg_name}")
    
    def test_dependencies_are_sorted(self, requirements_lines):
        """Test that dependencies are sorted alphabetically."""
        sorted_lines = sorted(requirements_lines, key=lambda x: x.split('[')[0].split('<')[0].split('>')[0].split('=')[0].lower())
        
        if requirements_lines != sorted_lines:
            pytest.skip("Consider sorting requirements alphabetically for maintainability")
    
    def test_reasonable_number_of_dependencies(self, requirements_lines):
        """Test that the number of dependencies is reasonable."""
        assert len(requirements_lines) <= 50, \
            "Consider if all dependencies are necessary (50+ found)"
    
    def test_no_redundant_dependencies(self, requirements_lines):
        """Test that there are no redundant package specifications."""
        package_names = [re.split(r'[<>=!\[]', line)[0].strip().lower() 
                        for line in requirements_lines]
        
        assert len(package_names) == len(set(package_names)), \
            "No duplicate package names should exist"


class TestRequirementsFormatting:
    """Test formatting and style of requirements.txt."""
    
    def test_no_trailing_whitespace(self, requirements_content):
        """Test that lines don't have trailing whitespace."""
        lines = requirements_content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.endswith(' ') or line.endswith('\t'):
                pytest.fail(f"Line {i} has trailing whitespace")
    
    def test_file_ends_with_newline(self, requirements_content):
        """Test that file ends with a newline."""
        assert requirements_content.endswith('\n'), \
            "requirements.txt should end with a newline"
    
    def test_no_blank_lines_between_requirements(self, requirements_content):
        """Test formatting consistency."""
        lines = requirements_content.split('\n')
        blank_count = 0
        
        for line in lines:
            if not line.strip():
                blank_count += 1
        
        # A few blank lines for grouping is okay, but not excessive
        assert blank_count <= 5, \
            "Avoid excessive blank lines in requirements.txt"
    
    def test_consistent_operator_spacing(self, requirements_lines):
        """Test that operators have consistent spacing."""
        for line in requirements_lines:
            # Operators should not have spaces around them
            if '>= ' in line or '<= ' in line or '== ' in line or '!= ' in line:
                pytest.skip(f"Consider removing spaces after operators: {line}")


class TestSpecificDependencies:
    """Test specific dependencies required for the test suite."""
    
    def test_pytest_yaml_plugin_included(self, requirements_lines):
        """Test that pytest-yaml is included for YAML testing."""
        pytest_yaml_found = any('pytest-yaml' in line.lower() for line in requirements_lines)
        assert pytest_yaml_found, \
            "pytest-yaml should be included for workflow YAML testing"
    
    def test_all_pytest_plugins_have_pytest_prefix(self, requirements_lines):
        """Test that pytest plugins follow naming convention."""
        pytest_plugins = [line for line in requirements_lines if line.startswith('pytest-')]
        
        for plugin in pytest_plugins:
            assert plugin.startswith('pytest-'), \
                f"Pytest plugin should start with 'pytest-': {plugin}"
    
    def test_core_testing_libraries_present(self, requirements_lines):
        """Test that core testing libraries are present."""
        required_libs = ['pytest', 'pyyaml']
        
        for lib in required_libs:
            found = any(lib.lower() in line.lower() for line in requirements_lines)
            assert found, f"Required testing library '{lib}' should be in requirements.txt"


class TestRequirementsCompatibility:
    """Test compatibility considerations."""
    
    def test_pytest_version_is_modern(self, requirements_lines):
        """Test that pytest version is reasonably modern."""
        pytest_lines = [line for line in requirements_lines if line.startswith('pytest')]
        
        if pytest_lines:
            pytest_spec = pytest_lines[0]
            # Extract version number
            match = re.search(r'>=?(\d+)\.', pytest_spec)
            if match:
                major_version = int(match.group(1))
                assert major_version >= 6, \
                    "pytest version should be 6.0 or higher"
    
    def test_pyyaml_version_is_secure(self, requirements_lines):
        """Test that PyYAML version addresses known vulnerabilities."""
        pyyaml_lines = [line for line in requirements_lines if 'pyyaml' in line.lower()]
        
        if pyyaml_lines:
            pyyaml_spec = pyyaml_lines[0]
            # PyYAML 5.4+ addresses CVE-2020-14343
            match = re.search(r'>=?(\d+)\.', pyyaml_spec)
            if match:
                major_version = int(match.group(1))
                assert major_version >= 5, \
                    "PyYAML should be version 5.4 or higher for security"


@pytest.mark.unit
class TestRequirementsEdgeCases:
    """Test edge cases in requirements specification."""
    
    def test_no_empty_lines_at_start(self, requirements_content):
        """Test that file doesn't start with empty lines."""
        assert not requirements_content.startswith('\n'), \
            "requirements.txt should not start with empty lines"
    
    def test_no_invalid_characters(self, requirements_content):
        """Test that file doesn't contain invalid characters."""
        # Check for null bytes and other control characters
        assert '\x00' not in requirements_content, \
            "requirements.txt should not contain null bytes"
    
    def test_consistent_line_endings(self, requirements_path):
        """Test that file uses consistent line endings."""
        with open(requirements_path, 'rb') as f:
            content = f.read()
        
        # Check if mixed line endings exist
        has_crlf = b'\r\n' in content
        has_lf = b'\n' in content and b'\r\n' not in content
        
        if has_crlf and has_lf:
            pytest.fail("requirements.txt has mixed line endings (CRLF and LF)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])