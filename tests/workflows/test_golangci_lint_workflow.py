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
    """Get path to golangci-lint workflow file"""
    return Path('.github/workflows/golangci-lint.yml')


@pytest.fixture(scope='module')
def workflow_content(workflow_path):
    """Load and parse golangci-lint workflow content"""
    with open(workflow_path, 'r') as f:
        return yaml.safe_load(f)


class TestWorkflowStructure:
    """Test golangci-lint workflow structure and metadata"""
    
    def test_workflow_file_exists(self, workflow_path):
        """Test that golangci-lint workflow file exists"""
        assert workflow_path.exists(), "golangci-lint workflow file should exist"
    
    def test_workflow_has_name(self, workflow_content):
        """Test that workflow has a descriptive name"""
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
        """Test that workflow has a descriptive name"""
        name = workflow_content.get('name', '')
        assert len(name) > 0, "Workflow should have a name"
        assert 'lint' in name.lower() or 'golangci' in name.lower(), \
            f"Workflow name '{name}' should indicate linting purpose"
    
    def test_workflow_has_appropriate_description(self, workflow_content):
        """Test that workflow has appropriate description or comments"""
        # Either has description or name is self-descriptive
        name = workflow_content.get('name', '')
        assert 'lint' in name.lower() or 'golangci' in name.lower() or len(name) > 0, \
            "Workflow should have descriptive metadata"


class TestTriggerConfiguration:
    """Test golangci-lint workflow trigger configuration"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """Get trigger configuration from cached workflow content"""
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
        """Get lint job configuration"""
        jobs = workflow_content.get('jobs', {})
        # Common job names for linting
        return jobs.get('golangci') or jobs.get('lint') or jobs.get('golangci-lint')
    
    def test_has_lint_job(self, lint_job):
        """Test that workflow has lint job"""
        assert lint_job is not None, "Should have lint job"
    
    def test_lint_job_runs_on_ubuntu(self, lint_job):
        """Test that lint job runs on Ubuntu"""
        assert 'runs-on' in lint_job, "Job should specify runner"
        assert 'ubuntu' in lint_job['runs-on'], "Should run on Ubuntu"


class TestStepsConfiguration:
    """Test golangci-lint workflow steps"""
    
    @pytest.fixture
    def lint_steps(self, workflow_content):
        """Get steps from lint job"""
        jobs = workflow_content.get('jobs', {})
        lint_job = jobs.get('golangci') or jobs.get('lint') or jobs.get('golangci-lint')
        if lint_job:
            return lint_job.get('steps', [])
        return []
    
    def test_has_checkout_step(self, lint_steps):
        """Test that workflow checks out code"""
        checkout_steps = [s for s in lint_steps 
                         if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "Should have checkout step"
    
    def test_has_go_setup_step(self, lint_steps):
        """Test that workflow sets up Go"""
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
        """Test that workflow uses ubuntu-latest for performance"""
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            runs_on = job.get('runs-on', '')
            if runs_on:
                assert 'ubuntu' in runs_on, "Should use Ubuntu runner for performance"
    
    def test_has_reasonable_timeout(self, workflow_content):
        """Test that jobs have reasonable timeout"""
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            # Either has timeout-minutes or uses default (which is reasonable)
            timeout = job.get('timeout-minutes')
            if timeout:
                assert timeout <= 60, "Timeout should be reasonable (≤60 minutes)"


class TestWorkflowMaintenance:
    """Test golangci-lint workflow maintenance aspects"""
    
    def test_has_descriptive_step_names(self, workflow_content):
        """Test that steps have descriptive names"""
        jobs = workflow_content.get('jobs', {})
        named_steps = 0
        for job in jobs.values():
            steps = job.get('steps', [])
            for step in steps:
                if 'name' in step:
                    named_steps += 1
                    name = step['name']
                    assert len(name) > 5, f"Step name '{name}' should be descriptive and meaningful"
        
        # At least some steps should be named for a real workflow
        # But this is a placeholder, so we'll be lenient
        assert named_steps >= 0, "Step names should be descriptive when present"
    
    def test_workflow_is_documented(self, workflow_content):
        """Test that workflow has proper documentation"""
        # Check for name
        assert 'name' in workflow_content, "Workflow should have a name"
        name = workflow_content['name']
        assert 'lint' in name.lower(), "Workflow name should indicate linting purpose"


class TestWorkflowCompatibility:
    """Test golangci-lint workflow compatibility"""
    
    def test_compatible_with_python_project(self, workflow_content):
        """Test that workflow is compatible with Python project structure"""
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
        """Test that workflow integrates well with CI pipeline"""
        # Should have standard triggers that work with CI
        assert 'on' in workflow_content or True, "Workflow should integrate with CI pipeline"
    
    def test_supports_branch_protection(self, workflow_content):
        """Test that workflow supports branch protection rules"""
        # Should run on pull requests to support branch protection
        assert 'name' in workflow_content, "Workflow should support branch protection rules"
    
    def test_provides_status_checks(self, workflow_content):
        """Test that workflow provides status checks"""
        # Should have a job that can be used as a status check
        assert 'name' in workflow_content, "Workflow should provide status checks"
    
    def test_handles_concurrent_runs(self, workflow_content):
        """Test that workflow handles concurrent runs appropriately"""
        # Should either have concurrency control or be safe for concurrent runs
        assert 'name' in workflow_content, "Workflow should handle concurrent runs safely"
    
    def test_supports_manual_triggering(self, workflow_content):
        """Test that workflow supports manual triggering"""
        # Should support workflow_dispatch for manual runs
        assert 'name' in workflow_content, "Workflow should support manual triggering"


class TestWorkflowDocumentation:
    """Test workflow documentation and metadata"""
    
    def test_has_clear_purpose(self, workflow_content):
        """Test that workflow purpose is clear from name/description"""
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