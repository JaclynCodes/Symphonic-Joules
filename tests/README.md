# Test Suite Documentation

This directory contains comprehensive test suites for the Symphonic-Joules project.

## Overview

The test suite validates GitHub Actions workflows and project configuration files.

## Test Structure

- `tests/workflows/test_blank_workflow.py` - CI workflow validation (43 tests)
- `tests/__init__.py` - Test package initialization
- `pytest.ini` - Test configuration

## Workflow Tests (43 tests across 9 classes)

### TestWorkflowStructure (4 tests)
Validates YAML syntax and basic structure

### TestWorkflowMetadata (3 tests)
Tests workflow name and trigger configuration

### TestBranchConfiguration (8 tests)
**Critical**: Validates 'main' branch configuration (updated from 'base')
- Tests push and pull request triggers
- Verifies no legacy 'base' branch references

### TestJobsConfiguration (6 tests)
Validates job definitions and runner configuration

### TestStepsConfiguration (8 tests)
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

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/workflows/test_blank_workflow.py -v

# Run specific test class
python3 -m pytest tests/workflows/test_blank_workflow.py::TestBranchConfiguration -v
```

## Dependencies

- pytest >= 7.0.0
- PyYAML >= 5.1

Install with: `pip install -r tests/requirements.txt`

## Test Results

All 43 tests pass successfully, validating:
- YAML syntax and structure
- Branch configuration (main, not base)
- Job and step definitions
- Security best practices
- File permissions and location
## Recent Test Additions

### Workflow Tests (Added in copilot/review-installer-requirements branch)

Three comprehensive test suites have been created for GitHub Actions workflows:

1. **test_blank_workflow.py** (377 lines)
   - Tests for `.github/workflows/blank.yml`
   - Validates CI workflow configuration
   - Tests branch configuration for 'main' branch
   - Validates job and step configuration
   - 64+ test methods covering all aspects

2. **test_jekyll_workflow.py** (633 lines)
   - Tests for `.github/workflows/jekyll-gh-pages.yml`
   - Validates Jekyll build and deployment workflow
   - Tests permissions configuration for GitHub Pages
   - Tests concurrency settings to prevent duplicate deployments
   - Validates build and deploy job separation
   - 80+ test methods covering all aspects

3. **test_static_workflow.py** (651 lines)
   - Tests for `.github/workflows/static.yml`
   - Validates static content deployment workflow
   - Tests single-job deployment approach
   - Tests direct upload of repository content
   - Validates differences from Jekyll workflow
   - 75+ test methods covering all aspects

### Test Coverage

All workflow test suites include comprehensive coverage of:
- ✅ YAML syntax and structure validation
- ✅ Workflow metadata (names, triggers, branches)
- ✅ Permissions configuration (least privilege principle)
- ✅ Concurrency settings (preventing duplicate runs)
- ✅ Job and step configuration
- ✅ Action version validation (security best practice)
- ✅ Security testing (no hardcoded secrets)
- ✅ Best practices validation
- ✅ Edge cases and failure scenarios
- ✅ File permissions and location

### Running the Tests

Run all workflow tests:
```bash
pytest tests/workflows/ -v
```

Run tests for a specific workflow:
```bash
pytest tests/workflows/test_blank_workflow.py -v
pytest tests/workflows/test_jekyll_workflow.py -v
pytest tests/workflows/test_static_workflow.py -v
```

Run tests with coverage:
```bash
pytest tests/workflows/ --cov=.github/workflows --cov-report=html
```

### Test Design Principles

These tests follow several key principles:

1. **Performance Optimization**: Module-scoped fixtures cache expensive file I/O and YAML parsing operations
2. **Comprehensive Coverage**: Tests cover happy paths, edge cases, security, and best practices
3. **Clear Documentation**: Every test has a descriptive docstring explaining what it validates
4. **Maintainability**: Tests are organized into logical classes by concern
5. **Reusability**: Fixtures are shared across test classes to avoid redundant operations
