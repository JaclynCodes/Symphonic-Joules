# Test Suite Documentation

This directory contains comprehensive test suites for the Symphonic-Joules project.

## Overview

The test suite validates GitHub Actions workflows and project configuration files with comprehensive coverage of structure, security, and best practices.

## Test Structure

### Workflow Tests

- `tests/workflows/test_blank_workflow.py` - CI workflow validation (37 tests, 9 test classes)
- `tests/workflows/test_jekyll_workflow.py` - Jekyll/GitHub Pages deployment validation (71 tests, 15 test classes)
- `tests/workflows/test_static_workflow.py` - Static content deployment validation (79 tests, 16 test classes)
- `tests/workflows/test_codeql_workflow.py` - CodeQL security analysis validation (30 tests, 8 test classes)
- `tests/workflows/test_golangci_lint_workflow.py` - Go linting workflow validation (29 tests, 10 test classes)
- `tests/workflows/test_license_check_workflow.py` - License checking workflow validation (31 tests, 8 test classes)
- `tests/workflows/test_new_workflow_tests.py` - Validation tests for newly added workflow test files

### Configuration Files

- `tests/__init__.py` - Test package initialization
- `pytest.ini` - Root-level test configuration
- `tests/pytest.ini` - Test-specific configuration with markers
- `tests/requirements.txt` - Test dependencies

## Test Coverage Summary

**Total Workflow Tests: 277 tests across 66 test classes**

**Total Test Suite: 435 tests** (including validation and meta-tests)

### Blank Workflow Tests (43 tests)

Tests for `.github/workflows/blank.yml` - CI workflow

#### TestWorkflowStructure (4 tests)
Validates YAML syntax and basic structure

#### TestWorkflowMetadata (3 tests)
Tests workflow name and trigger configuration

#### TestBranchConfiguration (8 tests)
**Critical**: Validates 'main' branch configuration
- Tests push and pull request triggers
- Verifies no legacy 'base' branch references

#### TestJobsConfiguration (6 tests)
Validates job definitions and runner configuration

#### TestStepsConfiguration (8 tests)
Validates individual workflow steps and actions

#### TestWorkflowComments (3 tests)
Validates documentation and badge references

#### TestEdgeCases (6 tests)
Tests YAML formatting and consistency

#### TestWorkflowSecurity (2 tests)
Validates security best practices

#### TestWorkflowFilePermissions (3 tests)
Tests file location and permissions

### Jekyll Workflow Tests (72 tests)

Tests for `.github/workflows/jekyll-gh-pages.yml` - Jekyll site deployment

#### TestWorkflowStructure (5 tests)
Validates YAML syntax, structure, and GitHub Pages-specific sections

#### TestWorkflowMetadata (3 tests)
Tests workflow naming conventions for Jekyll deployment

#### TestTriggerConfiguration (5 tests)
Validates push and workflow_dispatch triggers

#### TestPermissionsConfiguration (5 tests)
Tests OIDC permissions for secure GitHub Pages deployment

#### TestConcurrencyConfiguration (4 tests)
Validates concurrency control for production deployments

#### TestJobsConfiguration (6 tests)
Tests build and deploy job definitions

#### TestBuildJob (14 tests)
Comprehensive validation of Jekyll build process
- Checkout, setup pages, Jekyll build, artifact upload
- Parameter validation and version checking

#### TestDeployJob (8 tests)
Tests deployment job configuration and dependencies

#### TestWorkflowComments (4 tests)
Validates documentation quality

#### TestEdgeCases (6 tests)
Tests YAML formatting and edge cases

#### TestWorkflowSecurity (3 tests)
Validates OIDC authentication and security best practices

#### TestWorkflowFilePermissions (3 tests)
Tests file location and permissions

#### TestJobDependencies (2 tests)
Validates job dependency chain

#### TestStepNaming (2 tests)
Tests naming conventions for clarity

### Static Workflow Tests (75 tests)

Tests for `.github/workflows/static.yml` - Static content deployment

#### TestWorkflowStructure (5 tests)
Validates YAML syntax and GitHub Pages sections

#### TestWorkflowMetadata (4 tests)
Tests descriptive workflow naming

#### TestTriggerConfiguration (7 tests)
Validates trigger configuration (push, workflow_dispatch)

#### TestPermissionsConfiguration (7 tests)
Tests minimal permissions following least privilege principle

#### TestConcurrencyConfiguration (5 tests)
Validates production deployment concurrency control

#### TestJobsConfiguration (6 tests)
Tests single deploy job architecture

#### TestDeployJob (6 tests)
Tests deploy job environment and configuration

#### TestDeploySteps (14 tests)
Comprehensive validation of deployment steps
- Checkout, setup pages, artifact upload, deployment
- Step ordering and parameter validation

#### TestWorkflowComments (5 tests)
Validates documentation and clarity

#### TestEdgeCases (6 tests)
Tests YAML formatting, empty steps, and consistency

#### TestWorkflowSecurity (4 tests)
Validates OIDC, minimal permissions, and injection prevention

#### TestWorkflowFilePermissions (4 tests)
Tests file location and descriptive naming

#### TestWorkflowDifferencesFromJekyll (3 tests)
Validates appropriate differences from Jekyll workflow

#### TestStepNaming (2 tests)
Tests naming conventions and action-oriented names

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

# Run Jekyll workflow tests
python3 -m pytest tests/workflows/test_jekyll_workflow.py -v

# Run static workflow tests
python3 -m pytest tests/workflows/test_static_workflow.py -v
```

### Run Specific Test Classes
```bash
# Run branch configuration tests (blank workflow)
python3 -m pytest tests/workflows/test_blank_workflow.py::TestBranchConfiguration -v

# Run security tests (Jekyll workflow)
python3 -m pytest tests/workflows/test_jekyll_workflow.py::TestWorkflowSecurity -v

# Run permissions tests (static workflow)
python3 -m pytest tests/workflows/test_static_workflow.py::TestPermissionsConfiguration -v
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

## Test Dependencies

Install test dependencies with:

```bash
python -m pip install -r tests/requirements.txt
```

Required packages:
- pytest >= 7.0.0
- pytest-cov >= 3.0.0
- PyYAML >= 5.1

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
    python -m pip install -r tests/requirements.txt
    python -m pytest tests/ -v --tb=short
```

## Test Results Summary

All 190 tests pass successfully, validating:
- YAML syntax and structure across all workflows
- GitHub Actions best practices
- Security configurations (OIDC, permissions)
- Deployment workflows (Jekyll and static content)
- Branch configurations and triggers
- Job dependencies and step ordering
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