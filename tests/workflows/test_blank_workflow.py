"""
Comprehensive test suite for .github/workflows/blank.yml

This test suite validates the GitHub Actions workflow configuration including:
- YAML syntax and structure
- Workflow metadata (name, triggers)
- Branch configuration (specifically testing the 'main' branch requirement)
- Job definitions and runner configuration
- Step definitions and action versions
- Edge cases and failure scenarios
"""

import pytest
import yaml
import os
from pathlib import Path


# Module-level fixtures to cache expensive file I/O and parsing operations
@pytest.fixture(scope='module')
def workflow_path():
    """
    Module-scoped fixture for workflow file path.
    Computed once and shared across all tests in this module.
    """
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / '.github' / 'workflows' / 'blank.yml'


@pytest.fixture(scope='module')
def workflow_raw(workflow_path):
    """
    Module-scoped fixture for raw workflow content.
    File is read once and cached for all tests.
    """
    with open(workflow_path, 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def workflow_content(workflow_raw):
    """
    Module-scoped fixture for parsed workflow content.
    YAML parsing is done once and cached for all tests.
    Reuses workflow_raw to avoid redundant file I/O.
    """
    return yaml.safe_load(workflow_raw)


class TestWorkflowStructure:
    """Test the basic structure and syntax of the workflow file"""
    
    def test_workflow_file_exists(self, workflow_path):
        """Test that the workflow file exists at the expected location"""
        assert workflow_path.exists(), f"Workflow file not found at {workflow_path}"
        assert workflow_path.is_file(), f"Expected file but found directory at {workflow_path}"
    
    
    def test_workflow_is_not_empty(self, workflow_content):
        """Test that the workflow file is not empty"""
        assert workflow_content is not None, "Workflow content is None"
        assert len(workflow_content) > 0, "Workflow content is empty"
    
    def test_workflow_has_required_top_level_keys(self, workflow_content):
        """Test that workflow has all required top-level keys"""
        assert 'name' in workflow_content, "Workflow missing 'name' key"
        assert 'jobs' in workflow_content, "Workflow missing 'jobs' key"
        # 'on' key is parsed as boolean True by PyYAML, check for trigger configuration
        assert True in workflow_content or 'on' in workflow_content, "Workflow missing trigger configuration"


class TestWorkflowMetadata:
    """Test workflow metadata and configuration"""
    
    def test_workflow_name_is_defined(self, workflow_content):
        """Test that workflow has a name defined"""
        assert 'name' in workflow_content, "Workflow name not defined"
        assert isinstance(workflow_content['name'], str), "Workflow name must be a string"
        assert len(workflow_content['name']) > 0, "Workflow name cannot be empty"
    
    def test_workflow_name_is_ci(self, workflow_content):
        """Test that the workflow is named 'CI'"""
        assert workflow_content['name'] == 'CI', f"Expected workflow name 'CI', got '{workflow_content['name']}'"
    
    def test_workflow_has_triggers(self, workflow_content):
        """Test that workflow has trigger configuration"""
        # PyYAML parses 'on:' as True
        triggers = workflow_content.get(True) or workflow_content.get('on')
        assert triggers is not None, "Workflow has no trigger configuration"


class TestBranchConfiguration:
    """Test branch configuration - critical for the main branch change"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """Get trigger configuration from cached workflow content"""
        return workflow_content.get(True) or workflow_content.get('on')
    
    def _validate_branch_config(self, branches, trigger_name):
        """Helper method to validate branch configuration"""
        assert isinstance(branches, list), f"{trigger_name} branches must be a list"
        assert 'main' in branches, f"{trigger_name} trigger must include 'main' branch"
        assert 'base' not in branches, f"{trigger_name} trigger should not include 'base' branch (should be 'main')"
    
    def test_push_trigger_exists(self, triggers):
        """Test that push trigger is configured"""
        assert 'push' in triggers, "Push trigger not configured"
    
    def test_pull_request_trigger_exists(self, triggers):
        """Test that pull_request trigger is configured"""
        assert 'pull_request' in triggers, "Pull request trigger not configured"
    
    def test_workflow_dispatch_trigger_exists(self, triggers):
        """Test that workflow_dispatch trigger is configured"""
        assert 'workflow_dispatch' in triggers, "Workflow dispatch trigger not configured"
    
    def test_push_trigger_has_branches(self, triggers):
        """Test that push trigger has branch configuration"""
        push_config = triggers.get('push')
        assert push_config is not None, "Push trigger configuration is None"
        assert 'branches' in push_config, "Push trigger missing branches configuration"
    
    def test_pull_request_trigger_has_branches(self, triggers):
        """Test that pull_request trigger has branch configuration"""
        pr_config = triggers.get('pull_request')
        assert pr_config is not None, "Pull request trigger configuration is None"
        assert 'branches' in pr_config, "Pull request trigger missing branches configuration"
    
    def test_push_branches_is_main(self, triggers):
        """Test that push trigger is configured for 'main' branch (not 'base')"""
        push_branches = triggers['push']['branches']
        self._validate_branch_config(push_branches, "Push")
    
    def test_pull_request_branches_is_main(self, triggers):
        """Test that pull_request trigger is configured for 'main' branch (not 'base')"""
        pr_branches = triggers['pull_request']['branches']
        self._validate_branch_config(pr_branches, "Pull request")
    
    def test_only_main_branch_configured(self, triggers):
        """Test that only 'main' branch is configured (no other branches)"""
        push_branches = triggers['push']['branches']
        pr_branches = triggers['pull_request']['branches']
        
        assert len(push_branches) == 1, f"Expected exactly 1 push branch, got {len(push_branches)}"
        assert len(pr_branches) == 1, f"Expected exactly 1 PR branch, got {len(pr_branches)}"
        assert push_branches[0] == 'main', f"Expected 'main' branch for push, got '{push_branches[0]}'"
        assert pr_branches[0] == 'main', f"Expected 'main' branch for PR, got '{pr_branches[0]}'"


class TestJobsConfiguration:
    """Test jobs configuration"""
    
    @pytest.fixture
    def jobs(self, workflow_content):
        """Get jobs configuration from cached workflow content"""
        return workflow_content.get('jobs', {})
    
    def test_jobs_section_exists(self, workflow_content):
        """Test that jobs section exists"""
        assert 'jobs' in workflow_content, "Workflow missing 'jobs' section"
    
    def test_jobs_section_not_empty(self, jobs):
        """Test that jobs section is not empty"""
        assert len(jobs) > 0, "Jobs section is empty"
    
    def test_build_job_exists(self, jobs):
        """Test that 'build' job is defined"""
        assert 'build' in jobs, "Build job not defined"
    
    def test_build_job_has_runner(self, jobs):
        """Test that build job has a runner defined"""
        build_job = jobs.get('build', {})
        assert 'runs-on' in build_job, "Build job missing 'runs-on' configuration"
    
    def test_build_job_uses_ubuntu_latest(self, jobs):
        """Test that build job uses ubuntu-latest runner"""
        runner = jobs['build']['runs-on']
        assert runner == 'ubuntu-latest', f"Expected 'ubuntu-latest' runner, got '{runner}'"
    
    def test_build_job_has_steps(self, jobs):
        """Test that build job has steps defined"""
        build_job = jobs.get('build', {})
        assert 'steps' in build_job, "Build job missing 'steps'"
        assert isinstance(build_job['steps'], list), "Steps must be a list"
        assert len(build_job['steps']) > 0, "Build job has no steps"


class TestStepsConfiguration:
    """Test individual steps within the build job"""
    
    @pytest.fixture
    def steps(self, workflow_content):
        """Get workflow steps from cached workflow content"""
        return workflow_content['jobs']['build']['steps']
    
    def test_has_checkout_step(self, steps):
        """Test that workflow includes checkout action"""
        checkout_steps = [s for s in steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "No checkout step found"
    
    def test_checkout_uses_v4(self, steps):
        """Test that checkout action uses version 4"""
        checkout_steps = [s for s in steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "No checkout step found"
        checkout_action = checkout_steps[0]['uses']
        assert 'actions/checkout@v4' in checkout_action, f"Expected checkout@v4, got {checkout_action}"
    
    def test_has_minimum_three_steps(self, steps):
        """Test that workflow has at least 3 steps"""
        assert len(steps) >= 3, f"Expected at least 3 steps, got {len(steps)}"
    
    def test_all_steps_have_valid_structure(self, steps):
        """Test that all steps have either 'uses' or 'run' key"""
        for i, step in enumerate(steps):
            assert 'uses' in step or 'run' in step, f"Step {i} missing 'uses' or 'run' key"
    
    def test_named_steps_have_run_commands(self, steps):
        """Test that named steps have run commands"""
        for step in steps:
            if 'name' in step:
                assert 'run' in step, f"Named step '{step['name']}' missing 'run' command"
    
    def test_one_line_script_step_exists(self, steps):
        """Test that 'Run a one-line script' step exists"""
        one_line_steps = [s for s in steps if s.get('name') == 'Run a one-line script']
        assert len(one_line_steps) > 0, "One-line script step not found"
    
    def test_multi_line_script_step_exists(self, steps):
        """Test that 'Run a multi-line script' step exists"""
        multi_line_steps = [s for s in steps if s.get('name') == 'Run a multi-line script']
        assert len(multi_line_steps) > 0, "Multi-line script step not found"
    
    def test_script_steps_have_content(self, steps):
        """Test that script steps have actual commands"""
        for step in steps:
            if 'run' in step:
                run_command = step['run']
                assert isinstance(run_command, str), "Run command must be a string"
                assert len(run_command.strip()) > 0, "Run command cannot be empty"


class TestWorkflowComments:
    """Test comments and documentation in the workflow file"""
    
    def test_has_comments(self, workflow_raw):
        """Test that workflow file contains comments"""
        comment_lines = [line for line in workflow_raw.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) > 0, "Workflow should contain comments for documentation"
    
    def test_main_branch_comment_matches_config(self, workflow_raw):
        """Test that comments about main branch match the actual configuration"""
        # Check that comments mention 'main' branch - optimize by avoiding full lowercase conversion
        # Only convert to lowercase for case-insensitive search
        if 'main' not in workflow_raw and 'MAIN' not in workflow_raw and 'Main' not in workflow_raw:
            pytest.fail("Workflow should mention 'main' branch")
        
        # Ensure 'base' branch is not mentioned in active configuration
        lines = workflow_raw.split('\n')
        for line in lines:
            if 'branches:' in line:
                # Check the next line for branch configuration
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1]
                    if 'base' in next_line and not next_line.strip().startswith('#'):
                        pytest.fail("Found 'base' branch in active configuration (should be 'main')")
    
    def test_has_badge_reference(self, workflow_raw):
        """Test that workflow includes CI badge reference"""
        assert 'badge.svg' in workflow_raw, "Workflow should include badge reference"
        assert 'CI' in workflow_raw, "Workflow should reference CI badge"


class TestEdgeCases:
    """Test edge cases and potential failure scenarios"""
    
    def test_no_syntax_errors_in_yaml(self, workflow_content):
        """Test that there are no YAML syntax errors"""
        # If workflow_content fixture loaded successfully, YAML is valid
        # This test validates that the fixture itself works properly
        assert workflow_content is not None, "YAML content should be loaded"
    
    def test_no_tabs_in_yaml(self, workflow_raw):
        """Test that workflow file doesn't use tabs (YAML should use spaces)"""
        assert '\t' not in workflow_raw, "YAML file should use spaces, not tabs"
    
    def test_consistent_indentation(self, workflow_raw):
        """Test that indentation is consistent throughout the file"""
        lines = workflow_raw.split('\n')
        
        # Check that indentation is consistent (multiples of 2)
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    assert leading_spaces % 2 == 0, f"Line {i} has inconsistent indentation (not a multiple of 2)"
    
    def test_no_duplicate_job_names(self, workflow_content):
        """Test that there are no duplicate job names"""
        jobs = workflow_content.get('jobs', {})
        job_names = list(jobs.keys())
        assert len(job_names) == len(set(job_names)), "Duplicate job names found"
    
    def test_no_duplicate_step_names_in_job(self, workflow_content):
        """Test that there are no duplicate step names within a job"""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            step_names = [s.get('name') for s in steps if 'name' in s]
            assert len(step_names) == len(set(step_names)), f"Duplicate step names in job '{job_name}'"
    
    def test_runner_is_valid(self, workflow_content):
        """Test that runner configuration is valid"""
        jobs = workflow_content.get('jobs', {})
        valid_runners = [
            'ubuntu-latest', 'ubuntu-22.04', 'ubuntu-20.04',
            'windows-latest', 'windows-2022', 'windows-2019',
            'macos-latest', 'macos-13', 'macos-12', 'macos-11'
        ]
        
        for job_name, job_config in jobs.items():
            runner = job_config.get('runs-on')
            if isinstance(runner, str):
                assert runner in valid_runners, f"Invalid runner '{runner}' in job '{job_name}'"


class TestWorkflowSecurity:
    """Test security aspects of the workflow"""
    
    def test_no_hardcoded_secrets(self, workflow_raw):
        """Test that workflow doesn't contain hardcoded secrets"""
        suspicious_patterns = ['password', 'token', 'api_key', 'secret']
        lower_content = workflow_raw.lower()
        
        for pattern in suspicious_patterns:
            if pattern in lower_content:
                # Make sure it's not in a comment or using secrets context
                lines = workflow_raw.split('\n')
                for line in lines:
                    if pattern in line.lower() and not line.strip().startswith('#'):
                        # Check if it's using GitHub secrets context
                        assert 'secrets.' in line or '${{' in line, \
                            f"Potential hardcoded secret pattern '{pattern}' found"
    
    def test_checkout_action_is_pinned_or_versioned(self, workflow_content):
        """Test that actions use version tags (security best practice)"""
        jobs = workflow_content.get('jobs', {})
        for _job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    action = step['uses']
                    # Should have version (@ symbol)
                    assert '@' in action, f"Action '{action}' should specify a version"


class TestWorkflowFilePermissions:
    """Test file permissions and location"""
    
    def test_workflow_in_correct_directory(self, workflow_path):
        """Test that workflow is in .github/workflows directory"""
        assert '.github' in workflow_path.parts, "Workflow must be in .github directory"
        assert 'workflows' in workflow_path.parts, "Workflow must be in workflows subdirectory"
    
    def test_workflow_has_yml_extension(self, workflow_path):
        """Test that workflow file has .yml or .yaml extension"""
        assert workflow_path.suffix in ['.yml', '.yaml'], "Workflow must have .yml or .yaml extension"
    
    def test_workflow_file_is_readable(self, workflow_path):
        """Test that workflow file is readable"""
        assert os.access(workflow_path, os.R_OK), "Workflow file must be readable"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])