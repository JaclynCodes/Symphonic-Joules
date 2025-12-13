# Test Suite Documentation

This directory contains comprehensive test suites for the Symphonic-Joules project.

## Overview

The test suite validates the primary CI GitHub Actions workflow with coverage of structure, security, and best practices.

## Test Structure

### Workflow Tests

- `tests/workflows/test_blank_workflow.py` - CI workflow validation (37 tests, 9 test classes)

### Configuration Files

- `tests/__init__.py` - Test package initialization
- `pytest.ini` - Root-level test configuration
- `tests/pytest.ini` - Test-specific configuration with markers
- `tests/requirements.txt` - Test dependencies

## Dependencies

Install test dependencies with:

```bash
pip install -r tests/requirements.txt
```

Required packages:
- pytest >= 7.0.0
- pytest-cov >= 3.0.0
- PyYAML >= 5.1

## Test Coverage Summary

**Total Tests: 37 across 9 test classes**

### Blank Workflow Tests (37 tests)

Tests for `.github/workflows/blank.yml` - CI workflow

### TestWorkflowStructure (3 tests)
Validates YAML syntax and basic structure

### TestWorkflowMetadata (3 tests)
Tests workflow name and trigger configuration

### TestBranchConfiguration (4 tests)
**Critical**: Validates 'main' branch configuration
- Tests push and pull request triggers
- Verifies no legacy 'base' branch references

### TestJobsConfiguration (6 tests)
Validates job definitions and runner configuration

### TestStepsConfiguration (7 tests)
Validates individual workflow steps and actions

### TestWorkflowComments (3 tests)
Validates documentation and badge references

### TestEdgeCases (6 tests)
Tests YAML formatting and consistency

### TestWorkflowSecurity (2 tests)
Validates security best practices

### TestWorkflowFilePermissions (3 tests)
Tests file location and permissions

## Running Tests

### Run All Tests
```bash
# Run all tests with verbose output
python3 -m pytest tests/ -v

# Run with coverage report
python3 -m pytest tests/ -v --cov=.github/workflows --cov-report=html
```

### Run Specific Test Files
```bash
# Run blank workflow tests
python3 -m pytest tests/workflows/test_blank_workflow.py -v
```

### Run Specific Test Classes
```bash
# Run branch configuration tests (blank workflow)
python3 -m pytest tests/workflows/test_blank_workflow.py::TestBranchConfiguration -v
```

### Run Tests with Markers
```bash
# Run only workflow tests
python3 -m pytest -m workflows -v

# Run only unit tests
python3 -m pytest -m unit -v

# Run integration tests
python3 -m pytest -m integration -v
```

### Run Tests with Specific Patterns
```bash
# Run all security-related tests
python3 -m pytest -k security -v

# Run all permission-related tests
python3 -m pytest -k permission -v

# Run all edge case tests
python3 -m pytest -k edge -v
```

## Test Markers

The following pytest markers are available:

- `@pytest.mark.workflows` - Marks tests as workflow tests
- `@pytest.mark.integration` - Marks tests as integration tests
- `@pytest.mark.unit` - Marks tests as unit tests

## Test Design Principles

### Module-Scoped Fixtures
All test suites use module-scoped fixtures to cache expensive operations:
- File I/O operations (reading workflow files)
- YAML parsing
- Data extraction

This improves test performance significantly (single parse per module vs. per test).

### Comprehensive Coverage
Tests cover:
- **Happy path**: Standard workflow execution
- **Edge cases**: Empty sections, malformed input, boundary conditions
- **Security**: Permissions, OIDC, secret handling, injection vulnerabilities
- **Best practices**: Version pinning, naming conventions, documentation
- **Failure scenarios**: Missing configuration, invalid values, dependency issues

### Clear Test Organization
- Grouped by functionality (Structure, Metadata, Configuration, Security, etc.)
- Descriptive test names following pattern: `test_<what>_<expected_behavior>`
- Helper methods for complex validation logic
- Parameterized tests for reducing duplication

### Performance Optimization
- Module-scoped fixtures minimize redundant operations
- Efficient search patterns using list comprehensions
- Selective file reading (avoid reading large files unnecessarily)
- Cached parsing results shared across tests

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow step
- name: Run Tests
  run: |
    pip install -r tests/requirements.txt
    pytest tests/ -v --tb=short
```

## Test Results Summary

All 37 tests pass successfully, validating:
- YAML syntax and structure for the CI workflow
- GitHub Actions best practices
- Branch configurations and triggers
- Job definitions, runner configuration, and step ordering
- File permissions and locations
- Documentation quality and clarity

## Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Use module-scoped fixtures for expensive operations
3. Group related tests in classes
4. Add descriptive docstrings
5. Include both positive and negative test cases
6. Update this README with new test coverage information
7. Ensure tests are idempotent and can run in any order

## Future Test Coverage

Planned additions:
- Integration tests for actual workflow execution (when applicable)
- Performance benchmarks for workflow execution times
- Validation of workflow outputs and artifacts
- Cross-workflow consistency checks
- Documentation link validation
- Configuration file schema validation
