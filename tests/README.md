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