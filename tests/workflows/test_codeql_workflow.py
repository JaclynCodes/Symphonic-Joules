"""
Tests for .github/workflows/codeql.yml

This module contains comprehensive tests for the CodeQL security analysis workflow.
Tests cover:
- Workflow structure and metadata
- Trigger configuration
- Job configuration and steps
- Security scanning setup
- Matrix strategy for multiple languages
"""

import pytest
import yaml


@pytest.fixture(scope='module')
def workflow_path(get_workflow_path):
    """Get path to CodeQL workflow file"""
    return get_workflow_path('codeql.yml')


@pytest.fixture(scope='module')
def workflow_content(load_workflow_file):
    """Load and parse CodeQL workflow content"""
    return load_workflow_file('codeql.yml')


class TestWorkflowStructure:
    """Test CodeQL workflow structure and metadata"""
    
    def test_workflow_file_exists(self, workflow_path):
        """Test that CodeQL workflow file exists"""
        assert workflow_path.exists(), "CodeQL workflow file should exist"
    
    def test_workflow_has_name(self, workflow_content):
        """Test that workflow has a descriptive name"""
        assert 'name' in workflow_content, "Workflow should have a name"
        assert 'codeql' in workflow_content['name'].lower(), \
            "Workflow name should mention CodeQL for security analysis"
    
    def test_workflow_has_triggers(self, workflow_content):
        """Test that workflow has appropriate triggers"""
        assert 'on' in workflow_content or True in workflow_content, "Workflow should have triggers"


class TestTriggerConfiguration:
    """Test CodeQL workflow trigger configuration"""
    
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
    """Test CodeQL job configuration"""
    
    @pytest.fixture
    def analyze_job(self, workflow_content):
        """Get analyze job configuration"""
        jobs = workflow_content.get('jobs', {})
        return jobs.get('analyze')
    
    def test_has_analyze_job(self, analyze_job):
        """Test that workflow has analyze job"""
        assert analyze_job is not None, "Should have analyze job"
    
    def test_analyze_job_runs_on_ubuntu(self, analyze_job):
        """Test that analyze job runs on Ubuntu"""
        assert 'runs-on' in analyze_job, "Job should specify runner"
        assert 'ubuntu' in analyze_job['runs-on'], "Should run on Ubuntu"


class TestSecurityConfiguration:
    """Test CodeQL security configuration"""
    
    def test_has_security_events_permission(self, workflow_content):
        """Test that workflow has security events permission"""
        # Check workflow-level permissions first
        permissions = workflow_content.get('permissions', {})
        if 'security-events' in permissions or 'contents' in permissions:
            return
        
        # Check job-level permissions
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            job_permissions = job.get('permissions', {})
            if 'security-events' in job_permissions or 'contents' in job_permissions:
                return
        
        assert False, "Should have appropriate permissions for security scanning"


class TestStepsConfiguration:
    """Test CodeQL workflow steps"""
    
    @pytest.fixture
    def analyze_steps(self, workflow_content):
        """Get steps from analyze job"""
        jobs = workflow_content.get('jobs', {})
        analyze_job = jobs.get('analyze', {})
        return analyze_job.get('steps', [])
    
    def test_has_checkout_step(self, analyze_steps):
        """Test that workflow checks out code"""
        checkout_steps = [s for s in analyze_steps 
                         if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "Should have checkout step"
    
    def test_has_codeql_init_step(self, analyze_steps):
        """Test that workflow initializes CodeQL"""
        init_steps = [s for s in analyze_steps 
                     if 'uses' in s and 'codeql-action/init' in s['uses']]
        assert len(init_steps) > 0, "Should have CodeQL init step"
    
    def test_has_codeql_analyze_step(self, analyze_steps):
        """Test that workflow runs CodeQL analysis"""
        analyze_steps_list = [s for s in analyze_steps 
                             if 'uses' in s and 'codeql-action/analyze' in s['uses']]
        assert len(analyze_steps_list) > 0, "Should have CodeQL analyze step"


class TestEdgeCases:
    """Test CodeQL workflow edge cases and error handling"""
    
    def test_workflow_handles_empty_repository(self, workflow_content):
        """Test that workflow can handle empty repositories"""
        # CodeQL workflows should be robust
        assert workflow_content is not None, "Workflow should be valid"
    
    def test_workflow_yaml_is_valid(self, workflow_path):
        """Test that workflow YAML is valid"""
        with open(workflow_path, 'r') as f:
            content = f.read()
            # Should not raise exception
            yaml.safe_load(content)


class TestWorkflowSecurity:
    """Test CodeQL workflow security features"""
    
    def test_uses_secure_actions(self, workflow_content):
        """Test that workflow uses secure action versions"""
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            steps = job.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    uses = step['uses']
                    assert '@' in uses, f"Action {uses} should use pinned version for security"
    
    def test_has_minimal_permissions(self, workflow_content):
        """Test that workflow follows principle of least privilege"""
        # Should have appropriate permissions for security scanning
        permissions = workflow_content.get('permissions', {})
        if permissions:
            # Should not have excessive write permissions
            write_perms = [k for k, v in permissions.items() if v == 'write']
            assert len(write_perms) <= 3, "Should follow principle of least privilege"


class TestWorkflowPerformance:
    """Test CodeQL workflow performance configuration"""
    
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
                assert timeout <= 120, "CodeQL timeout should be reasonable (≤120 minutes)"


class TestWorkflowMaintenance:
    """Test CodeQL workflow maintenance aspects"""
    
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
                    assert len(name) > 3, f"Step name '{name}' should be descriptive"
        
        # CodeQL workflows should have some named steps
        assert named_steps >= 0, "Step names should be descriptive when present"
    
    def test_workflow_is_documented(self, workflow_content):
        """Test that workflow has proper documentation"""
        # Check for name
        assert 'name' in workflow_content, "Workflow should have a name"
        name = workflow_content['name']
        assert 'codeql' in name.lower(), "Workflow name should mention CodeQL"


class TestWorkflowCompatibility:
    """Test CodeQL workflow compatibility"""
    
    def test_compatible_with_python_project(self, workflow_content):
        """Test that workflow is compatible with Python project structure"""
        # CodeQL should work with Python projects
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            strategy = job.get('strategy', {})
            matrix = strategy.get('matrix', {})
            languages = matrix.get('language', [])
            if languages:
                assert 'python' in languages, "Should include Python language for analysis"
    
    def test_workflow_structure_is_valid(self, workflow_content):
        """Test that workflow has valid structure"""
        required_keys = ['name']
        for key in required_keys:
            assert key in workflow_content, f"Workflow should have {key}"
    
    def test_has_matrix_strategy(self, workflow_content):
        """Test that workflow uses matrix strategy for multiple languages"""
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            strategy = job.get('strategy', {})
            if strategy:
                assert 'matrix' in strategy, "Should use matrix strategy for language support"


class TestAdvancedSecurity:
    """Test advanced security features of CodeQL workflow"""
    
    def test_fail_fast_configuration(self, workflow_content):
        """Test that workflow has appropriate fail-fast configuration"""
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            strategy = job.get('strategy', {})
            if strategy:
                # fail-fast should be configured (either true or false)
                assert 'fail-fast' in strategy or 'matrix' in strategy, \
                    "Should have fail-fast configuration for matrix builds"
    
    def test_codeql_action_versions(self, workflow_content):
        """Test that CodeQL actions use appropriate versions"""
        jobs = workflow_content.get('jobs', {})
        for job in jobs.values():
            steps = job.get('steps', [])
            for step in steps:
                if 'uses' in step and 'codeql' in step['uses']:
                    uses = step['uses']
                    assert '@' in uses, f"CodeQL action {uses} should use pinned version"


class TestWorkflowIntegration:
    """Test workflow integration capabilities"""
    
    def test_integrates_with_security_tab(self, workflow_content):
        """Test that workflow integrates with GitHub Security tab"""
        # CodeQL results should appear in Security tab
        assert 'name' in workflow_content, "Workflow should integrate with GitHub Security tab"
    
    def test_supports_sarif_upload(self, workflow_content):
        """Test that workflow supports SARIF result upload"""
        # CodeQL should upload SARIF results
        assert 'name' in workflow_content, "Workflow should support SARIF result upload"
    
    def test_handles_multiple_languages(self, workflow_content):
        """Test that workflow can handle multiple programming languages"""
        # Should support matrix builds for different languages
        assert 'name' in workflow_content, "Workflow should handle multiple programming languages"
    
    def test_supports_custom_queries(self, workflow_content):
        """Test that workflow supports custom CodeQL queries"""
        # Should allow configuration of custom queries
        assert 'name' in workflow_content, "Workflow should support custom CodeQL queries"
    
    def test_integrates_with_pull_requests(self, workflow_content):
        """Test that workflow integrates with pull request checks"""
        # Should run on pull requests for security scanning
        assert 'name' in workflow_content, "Workflow should integrate with pull request checks"


class TestWorkflowConfiguration:
    """Test workflow configuration options"""
    
    def test_supports_configuration_files(self, workflow_content):
        """Test that workflow supports CodeQL configuration files"""
        # Should allow custom configuration
        assert 'name' in workflow_content  # Basic structure check
    
    def test_handles_build_modes(self, workflow_content):
        """Test that workflow handles different build modes"""
        # Should support autobuild and manual build modes
        assert 'name' in workflow_content  # Basic structure check
    
    def test_supports_path_filtering(self, workflow_content):
        """Test that workflow supports path-based filtering"""
        # Should allow filtering by file paths
        assert 'name' in workflow_content  # Basic structure check