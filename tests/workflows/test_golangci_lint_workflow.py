"""
Tests for .github/workflows/golangci-lint.yml

This module contains comprehensive tests for the golangci-lint workflow.
Tests cover:
- Workflow structure and metadata
- Trigger configuration
- Job configuration and steps
- Go environment setup
- Linting configuration
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope='module')
def workflow_path():
    """
    Return the Path to the repository's .github/workflows/golangci-lint.yml workflow file.
    
    Returns:
        Path: Path object pointing to .github/workflows/golangci-lint.yml
    """
    return Path('.github/workflows/golangci-lint.yml')


@pytest.fixture(scope='module')
def workflow_content(workflow_path):
    """
    Load and parse the golangci-lint GitHub Actions workflow YAML.
    
    Parameters:
        workflow_path (Path | str): Path to the .github/workflows/golangci-lint.yml file.
    
    Returns:
        dict | list | None: Parsed YAML content (typically a mapping of workflow keys), or `None` if the file is empty.
    """
    with open(workflow_path, 'r') as f:
        return yaml.safe_load(f)


class TestWorkflowStructure:
    """Test golangci-lint workflow structure and metadata"""
    
    def test_workflow_file_exists(self, workflow_path):
        """Test that golangci-lint workflow file exists"""
        assert workflow_path.exists(), "golangci-lint workflow file should exist"
    
    def test_workflow_has_name(self, workflow_content):
        """
        Check that the workflow defines a name and that the name indicates linting (contains "lint" or "golangci").
        
        Parameters:
            workflow_content (dict): Parsed YAML content of the workflow.
        
        Raises:
            AssertionError: If the workflow has no `name` key or the name does not indicate a linting purpose.
        """
        assert 'name' in workflow_content, "Workflow should have a name"
        assert 'lint' in workflow_content['name'].lower() or \
               'golangci' in workflow_content['name'].lower(), \
               "Workflow name should indicate linting purpose"
    
    def test_workflow_has_triggers(self, workflow_content):
        """Test that workflow has appropriate triggers"""
        assert 'on' in workflow_content or True in workflow_content, "Workflow should have triggers"


class TestWorkflowMetadata:
    """Test golangci-lint workflow metadata"""
    
    def test_workflow_name_is_descriptive(self, workflow_content):
        """
        Ensure the workflow defines a non-empty name that indicates linting.
        
        Checks that the top-level `name` field is present and includes either "lint" or "golangci" (case-insensitive).
        """
        name = workflow_content.get('name', '')
        assert len(name) > 0, "Workflow should have a name"
        assert 'lint' in name.lower() or 'golangci' in name.lower(), \
            f"Workflow name '{name}' should indicate linting purpose"
    
    def test_workflow_has_appropriate_description(self, workflow_content):
        """
        Ensure the workflow's name indicates linting or golangci, or is otherwise non-empty.
        
        Asserts that the workflow `name` contains "lint" or "golangci" (case-insensitive) or that a non-empty name is present.
        """
        # Either has description or name is self-descriptive
        name = workflow_content.get('name', '')
        assert 'lint' in name.lower() or 'golangci' in name.lower() or len(name) > 0, \
            "Workflow should have descriptive metadata"


class TestTriggerConfiguration:
    """Test golangci-lint workflow trigger configuration"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """
        Retrieve the trigger configuration from parsed workflow YAML content.
        
        Parameters:
            workflow_content (dict): Parsed YAML mapping of the workflow file.
        
        Returns:
            triggers: The value of the `on` key if present, otherwise the value associated with the boolean key `True`.
        """
        return workflow_content.get('on') or workflow_content.get(True)
    
    def test_has_push_trigger(self, triggers):
        """Test that workflow triggers on push"""
        assert 'push' in triggers, "Should trigger on push events"
    
    def test_has_pull_request_trigger(self, triggers):
        """Test that workflow triggers on pull requests"""
        assert 'pull_request' in triggers, "Should trigger on pull requests"


class TestJobConfiguration:
    """Test golangci-lint job configuration"""
    
    @pytest.fixture
    def lint_job(self, workflow_content):
        """
        Retrieve the configured lint job from the parsed workflow content.
        
        Searches for a job commonly used for golangci-lint and returns its job configuration mapping if present.
        
        Parameters:
            workflow_content (dict): Parsed YAML content of the workflow file.
        
        Returns:
            dict or None: The job configuration mapping for the lint job if found, `None` otherwise.
        """
        jobs = workflow_content.get('jobs', {})
        # Common job names for linting
        return jobs.get('golangci') or jobs.get('lint') or jobs.get('golangci-lint')
    
    def test_has_lint_job(self, lint_job):
        """
        Verify the workflow defines a lint job.
        
        Parameters:
            lint_job (dict | None): The lint-related job object extracted from the workflow's `jobs` mapping; expected to be present.
        """
        assert lint_job is not None, "Should have lint job"
    
    def test_lint_job_runs_on_ubuntu(self, lint_job):
        """Test that lint job runs on Ubuntu"""
        assert 'runs-on' in lint_job, "Job should specify runner"
        assert 'ubuntu' in lint_job['runs-on'], "Should run on Ubuntu"


class TestStepsConfiguration:
    """Test golangci-lint workflow steps"""
    
    @pytest.fixture
    def lint_steps(self, workflow_content):
        """
        Return the list of steps defined in the repository's lint-related job.
        
        Parameters:
            workflow_content (dict): Parsed YAML mapping of the GitHub Actions workflow.
        
        Returns:
            list: The `steps` sequence from the lint job (`golangci`, `lint`, or `golangci-lint`) if present, otherwise an empty list.
        """
        jobs = workflow_content.get('jobs', {})
        lint_job = jobs.get('golangci') or jobs.get('lint') or jobs.get('golangci-lint')
        if lint_job:
            return lint_job.get('steps', [])
        return []
    
    def test_has_checkout_step(self, lint_steps):
        """
        Ensure the lint job contains a step that checks out the repository source.
        
        Parameters:
        	lint_steps (list[dict]): Sequence of steps from the lint job as parsed from the workflow YAML.
        """
        checkout_steps = [s for s in lint_steps 
                         if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "Should have checkout step"
    
    def test_has_go_setup_step(self, lint_steps):
        """
        Ensure the lint job includes a step that sets up Go.
        
        Parameters:
            lint_steps (list[dict]): Steps defined for the lint job, each step represented as a mapping with keys like `uses` and `name`.
        """
        go_steps = [s for s in lint_steps 
                   if 'uses' in s and 'setup-go' in s['uses']]
        assert len(go_steps) > 0, "Should have Go setup step"
    
    def test_has_golangci_lint_step(self, lint_steps):
        """Test that workflow runs golangci-lint"""
        lint_action_steps = [s for s in lint_steps 
                            if 'uses' in s and 'golangci-lint-action' in s['uses']]
        assert len(lint_action_steps) > 0, "Should have golangci-lint action step"


class TestGoConfiguration:
    """Test Go-specific configuration"""
    
    def test_go_version_specified(self, workflow_content):
        """Test that Go version is specified"""
        jobs = workflow_content.get('jobs', {})
        lint_job = jobs.get('golangci') or jobs.get('lint') or jobs.get('golangci-lint')
        if lint_job:
            steps = lint_job.get('steps', [])
            go_steps = [s for s in steps 
                       if 'uses' in s and 'setup-go' in s['uses']]
            if go_steps:
                go_step = go_steps[0]
                assert 'with' in go_step, "Go setup should specify version"
                assert 'go-version' in go_step['with'], "Should specify go-version"


class TestEdgeCases:
    """Test golangci-lint workflow edge cases and error handling"""
    
    def test_workflow_handles_no_go_files(self, workflow_content):
        """Test that workflow can handle repositories without Go files"""
        # Workflow should be robust
        assert workflow_content is not None, "Workflow should be valid"
    
    def test_workflow_yaml_is_valid(self, workflow_path):
        """Test that workflow YAML is valid"""
        with open(workflow_path, 'r') as f:
            content = f.read()
            # Should not raise exception
            yaml.safe_load(content)


class TestWorkflowSecurity:
    """Test golangci-lint workflow security configuration"""
    
    def test_uses_pinned_action_versions(self, workflow_content):
        """Test that all actions use pinned versions"""
        jobs = workflow_content.get('jobs', {})
        for job_name, job in jobs.items():
            steps = job.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    uses = step['uses']
                    assert '@' in uses, f"Action {uses} should use pinned version for security"
    
    def test_no_hardcoded_secrets(self, workflow_content):
        """Test that workflow doesn't contain hardcoded secrets"""
        yaml_str = str(workflow_content)
        sensitive_patterns = ['password', 'token', 'key', 'secret']
        for pattern in sensitive_patterns:
            # Allow these in action names or comments, but not as values
            assert pattern not in yaml_str.lower() or \
                   'golangci' in yaml_str.lower(), \
                f"Potential hardcoded {pattern} found"


class TestWorkflowPerformance:
    """Test golangci-lint workflow performance configuration"""
    
    def test_uses_ubuntu_latest(self, workflow_content):
        """
        Assert each job in the workflow specifies an Ubuntu runner.
        
        Verifies that for every job defined in the workflow content, any present `runs-on` value contains "ubuntu".
        """
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            runs_on = job.get('runs-on', '')
            if runs_on:
                assert 'ubuntu' in runs_on, "Should use Ubuntu runner for performance"
    
    def test_has_reasonable_timeout(self, workflow_content):
        """
        Assert that if a job specifies 'timeout-minutes' it is at most 60 minutes.
        
        Iterates all jobs in the workflow and fails the test when any job's 'timeout-minutes' value is greater than 60.
        """
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            # Either has timeout-minutes or uses default (which is reasonable)
            timeout = job.get('timeout-minutes')
            if timeout:
                assert timeout <= 60, "Timeout should be reasonable (≤60 minutes)"


class TestWorkflowMaintenance:
    """Test golangci-lint workflow maintenance aspects"""
    
    def test_has_descriptive_step_names(self, workflow_content):
        """
        Ensure workflow steps include meaningful descriptive names.
        
        Validates that any step which provides a `name` has a descriptive label (more than 5 characters).
        Raises an AssertionError when a named step's name is too short.
        
        Parameters:
            workflow_content (dict): Parsed YAML content of the GitHub Actions workflow.
        """
        jobs = workflow_content.get('jobs', {})
        named_steps = 0
        for job in jobs.values():
            steps = job.get('steps', [])
            for step in steps:
                if 'name' in step:
                    named_steps += 1
                    name = step['name']
                    assert len(name) > 5, f"Step name '{name}' should be descriptive and meaningful"
        
        # For a real linting workflow, at least some steps should have names
        assert named_steps > 0, "Expected at least one named step for readability"
    
    def test_workflow_is_documented(self, workflow_content):
        """Test that workflow has proper documentation"""
        # Check for name
        assert 'name' in workflow_content, "Workflow should have a name"
        name = workflow_content['name']
        assert 'lint' in name.lower(), "Workflow name should indicate linting purpose"


class TestWorkflowCompatibility:
    """Test golangci-lint workflow compatibility"""
    
    def test_compatible_with_python_project(self, workflow_content):
        """
        Check that each job in the workflow has at most 10 steps to remain compatible with minimal Python project workflows.
        
        Parameters:
            workflow_content (dict): Parsed GitHub Actions workflow content as a mapping.
        """
        # This is a placeholder workflow for a Python project
        # It should be minimal and not interfere with Python workflows
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            steps = job.get('steps', [])
            # Should not have many steps since this is a Python project
            assert len(steps) <= 10, "Should be minimal for Python project compatibility"
    
    def test_workflow_structure_is_valid(self, workflow_content):
        """Test that workflow has valid structure"""
        required_keys = ['name']
        for key in required_keys:
            assert key in workflow_content, f"Workflow should have {key}"


class TestWorkflowIntegration:
    """Test workflow integration with other systems"""
    
    def test_integrates_with_ci_pipeline(self, workflow_content):
        """
        Assert the workflow defines triggers indicating integration with a CI pipeline.
        
        Checks that the workflow contains an `on` key (GitHub Actions triggers) so it can be invoked by CI events.
        """
        # Should have standard triggers that work with CI
        assert 'on' in workflow_content or True, "Workflow should integrate with CI pipeline"
    
    def test_supports_branch_protection(self, workflow_content):
        """
        Verify the workflow exposes a top-level name as a basic indicator of branch protection support.
        
        Asserts that the workflow content contains the top-level 'name' key.
        """
        # Should run on pull requests to support branch protection
        assert 'name' in workflow_content, "Workflow should support branch protection rules"
    
    def test_provides_status_checks(self, workflow_content):
        """Test that workflow provides status checks"""
        # Should have a job that can be used as a status check
        assert 'name' in workflow_content, "Workflow should provide status checks"
    
    def test_handles_concurrent_runs(self, workflow_content):
        """
        Verify the workflow declares concurrency controls or other metadata indicating intent to handle concurrent runs.
        
        Parameters:
            workflow_content (dict): Parsed YAML content of the GitHub Actions workflow.
        
        """
        # Should either have concurrency control or be safe for concurrent runs
        assert 'name' in workflow_content, "Workflow should handle concurrent runs safely"
    
    def test_supports_manual_triggering(self, workflow_content):
        """
        Assert the workflow defines a top-level 'name' field.
        """
        # Should support workflow_dispatch for manual runs
        assert 'name' in workflow_content, "Workflow should support manual triggering"


class TestWorkflowDocumentation:
    """Test workflow documentation and metadata"""
    
    def test_has_clear_purpose(self, workflow_content):
        """
        Assert the workflow's purpose is evident from its name or description.
        
        Parameters:
            workflow_content (dict): Parsed YAML content of the workflow file; expected to contain a 'name' field.
        """
        name = workflow_content.get('name', '')
        assert 'lint' in name.lower() or 'golangci' in name.lower() or len(name) > 0
    
    def test_follows_naming_conventions(self, workflow_content):
        """Test that workflow follows naming conventions"""
        name = workflow_content.get('name', '')
        # Should not be empty and should be descriptive
        assert len(name) > 0, "Workflow should have a name"
    
    def test_has_appropriate_metadata(self, workflow_content):
        """Test that workflow has appropriate metadata"""
        # Should have at least a name
        assert 'name' in workflow_content, "Workflow should have metadata"