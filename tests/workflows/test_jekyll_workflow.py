"""
Comprehensive test suite for .github/workflows/jekyll-gh-pages.yml

This test suite validates the GitHub Actions workflow for Jekyll GitHub Pages deployment including:
- YAML syntax and structure
- Workflow metadata and permissions
- Trigger configuration (push to main, workflow_dispatch)
- Job definitions (build and deploy jobs)
- Step definitions and action versions
- Concurrency settings
- Environment configuration
- Edge cases and security considerations
"""

import pytest
import yaml
import os
from pathlib import Path


@pytest.fixture(scope='module')
def workflow_path():
    """Module-scoped fixture for workflow file path."""
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / '.github' / 'workflows' / 'jekyll-gh-pages.yml'


@pytest.fixture(scope='module')
def workflow_raw(workflow_path):
    """Module-scoped fixture for raw workflow content."""
    with open(workflow_path, 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def workflow_content(workflow_raw):
    """Module-scoped fixture for parsed workflow content."""
    return yaml.safe_load(workflow_raw)


class TestWorkflowStructure:
    """Test the basic structure and syntax of the workflow file"""
    
    def test_workflow_file_exists(self, workflow_path):
        """Test that the workflow file exists at the expected location"""
        assert workflow_path.exists(), f"Workflow file not found at {workflow_path}"
        assert workflow_path.is_file(), f"Expected file but found directory at {workflow_path}"
    
    def test_workflow_is_valid_yaml(self, workflow_content):
        """Test that the workflow file is valid YAML"""
        assert workflow_content is not None, "Workflow content is None"
        assert isinstance(workflow_content, dict), "Workflow content must be a dictionary"
    
    def test_workflow_has_required_keys(self, workflow_content):
        """Test that workflow has all required top-level keys"""
        assert 'name' in workflow_content, "Workflow missing 'name' key"
        assert 'jobs' in workflow_content, "Workflow missing 'jobs' key"
        # 'on' key is parsed as True by PyYAML
        assert True in workflow_content or 'on' in workflow_content, "Workflow missing trigger configuration"


class TestWorkflowMetadata:
    """Test workflow metadata and configuration"""
    
    def test_workflow_name_is_defined(self, workflow_content):
        """Test that workflow has a descriptive name"""
        assert 'name' in workflow_content, "Workflow name not defined"
        name = workflow_content['name']
        assert isinstance(name, str), "Workflow name must be a string"
        assert len(name) > 0, "Workflow name cannot be empty"
        assert 'Jekyll' in name or 'Pages' in name, "Workflow name should mention Jekyll or Pages"
    
    def test_workflow_name_matches_purpose(self, workflow_content):
        """Test that workflow name indicates Jekyll deployment purpose"""
        name = workflow_content['name']
        assert 'Jekyll' in name, f"Expected Jekyll in name, got '{name}'"
        assert 'Pages' in name or 'GitHub Pages' in name, "Name should mention GitHub Pages"


class TestTriggerConfiguration:
    """Test trigger configuration for the workflow"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """Get trigger configuration"""
        return workflow_content.get(True) or workflow_content.get('on')
    
    def test_has_push_trigger(self, triggers):
        """Test that workflow has push trigger"""
        assert 'push' in triggers, "Workflow should have push trigger"
    
    def test_has_workflow_dispatch_trigger(self, triggers):
        """Test that workflow has manual trigger"""
        assert 'workflow_dispatch' in triggers, "Workflow should support manual triggering"
    
    def test_push_trigger_targets_main_branch(self, triggers):
        """Test that push trigger targets main branch"""
        push_config = triggers.get('push')
        assert push_config is not None, "Push configuration is missing"
        assert 'branches' in push_config, "Push trigger missing branch configuration"
        branches = push_config['branches']
        assert isinstance(branches, list), "Branches must be a list"
        assert 'main' in branches, "Push trigger should target 'main' branch"
    
    def test_no_pull_request_trigger(self, triggers):
        """Test that workflow doesn't trigger on pull requests (deployment workflow)"""
        assert 'pull_request' not in triggers, "Deployment workflow should not trigger on PRs"


class TestPermissions:
    """Test GitHub token permissions configuration"""
    
    def test_has_permissions_section(self, workflow_content):
        """Test that workflow defines permissions"""
        assert 'permissions' in workflow_content, "Workflow should define permissions"
    
    def test_permissions_structure(self, workflow_content):
        """Test that permissions are properly structured"""
        permissions = workflow_content.get('permissions', {})
        assert isinstance(permissions, dict), "Permissions must be a dictionary"
        assert len(permissions) > 0, "Permissions should not be empty"
    
    def test_has_contents_read_permission(self, workflow_content):
        """Test that workflow has contents read permission"""
        permissions = workflow_content.get('permissions', {})
        assert 'contents' in permissions, "Should have 'contents' permission"
        assert permissions['contents'] == 'read', "Contents should be 'read'"
    
    def test_has_pages_write_permission(self, workflow_content):
        """Test that workflow has pages write permission"""
        permissions = workflow_content.get('permissions', {})
        assert 'pages' in permissions, "Should have 'pages' permission for deployment"
        assert permissions['pages'] == 'write', "Pages should have 'write' permission"
    
    def test_has_id_token_write_permission(self, workflow_content):
        """Test that workflow has id-token write permission"""
        permissions = workflow_content.get('permissions', {})
        assert 'id-token' in permissions, "Should have 'id-token' permission"
        assert permissions['id-token'] == 'write', "ID token should have 'write' permission"
    
    def test_follows_least_privilege_principle(self, workflow_content):
        """Test that only necessary permissions are granted"""
        permissions = workflow_content.get('permissions', {})
        expected_permissions = {'contents', 'pages', 'id-token'}
        actual_permissions = set(permissions.keys())
        
        # Should not have excessive permissions
        excessive = actual_permissions - expected_permissions
        assert len(excessive) == 0, f"Workflow has excessive permissions: {excessive}"


class TestConcurrencyConfiguration:
    """Test concurrency settings for deployment workflows"""
    
    def test_has_concurrency_configuration(self, workflow_content):
        """Test that workflow defines concurrency settings"""
        assert 'concurrency' in workflow_content, "Deployment workflow should have concurrency settings"
    
    def test_concurrency_group_is_defined(self, workflow_content):
        """Test that concurrency group is properly defined"""
        concurrency = workflow_content.get('concurrency', {})
        assert 'group' in concurrency, "Concurrency must define a group"
        assert concurrency['group'] == 'pages', "Concurrency group should be 'pages'"
    
    def test_cancel_in_progress_is_false(self, workflow_content):
        """Test that cancel-in-progress is set to false for production deployments"""
        concurrency = workflow_content.get('concurrency', {})
        assert 'cancel-in-progress' in concurrency, "Should specify cancel-in-progress behavior"
        assert concurrency['cancel-in-progress'] is False, \
            "Should not cancel in-progress deployments (production safety)"


class TestJobsConfiguration:
    """Test jobs configuration"""
    
    @pytest.fixture
    def jobs(self, workflow_content):
        """Get jobs configuration"""
        return workflow_content.get('jobs', {})
    
    def test_has_build_job(self, jobs):
        """Test that workflow has a build job"""
        assert 'build' in jobs, "Workflow should have 'build' job"
    
    def test_has_deploy_job(self, jobs):
        """Test that workflow has a deploy job"""
        assert 'deploy' in jobs, "Workflow should have 'deploy' job"
    
    def test_jobs_not_empty(self, jobs):
        """Test that jobs section is not empty"""
        assert len(jobs) > 0, "Jobs section should not be empty"
    
    def test_exactly_two_jobs(self, jobs):
        """Test that workflow has exactly two jobs (build and deploy)"""
        assert len(jobs) == 2, f"Expected 2 jobs (build, deploy), found {len(jobs)}"


class TestBuildJob:
    """Test the build job configuration"""
    
    @pytest.fixture
    def build_job(self, workflow_content):
        """Get build job configuration"""
        return workflow_content['jobs']['build']
    
    def test_build_job_has_runner(self, build_job):
        """Test that build job defines a runner"""
        assert 'runs-on' in build_job, "Build job must specify runner"
        assert build_job['runs-on'] == 'ubuntu-latest', "Build job should use ubuntu-latest"
    
    def test_build_job_has_steps(self, build_job):
        """Test that build job has steps defined"""
        assert 'steps' in build_job, "Build job must have steps"
        steps = build_job['steps']
        assert isinstance(steps, list), "Steps must be a list"
        assert len(steps) > 0, "Build job must have at least one step"
    
    def test_build_job_has_checkout_step(self, build_job):
        """Test that build job checks out code"""
        steps = build_job['steps']
        checkout_steps = [s for s in steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "Build job must checkout repository"
    
    def test_build_job_sets_up_pages(self, build_job):
        """Test that build job sets up GitHub Pages"""
        steps = build_job['steps']
        pages_steps = [s for s in steps if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(pages_steps) > 0, "Build job must configure GitHub Pages"
    
    def test_build_job_builds_with_jekyll(self, build_job):
        """Test that build job uses Jekyll build action"""
        steps = build_job['steps']
        jekyll_steps = [s for s in steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "Build job must use Jekyll build action"
    
    def test_build_job_uploads_artifact(self, build_job):
        """Test that build job uploads pages artifact"""
        steps = build_job['steps']
        upload_steps = [s for s in steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "Build job must upload artifact for deployment"
    
    def test_jekyll_build_has_source_and_destination(self, build_job):
        """Test that Jekyll build step specifies source and destination"""
        steps = build_job['steps']
        jekyll_steps = [s for s in steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "Jekyll build step not found"
        
        jekyll_step = jekyll_steps[0]
        assert 'with' in jekyll_step, "Jekyll build step should have 'with' configuration"
        config = jekyll_step['with']
        assert 'source' in config, "Jekyll build should specify source directory"
        assert 'destination' in config, "Jekyll build should specify destination directory"


class TestDeployJob:
    """Test the deploy job configuration"""
    
    @pytest.fixture
    def deploy_job(self, workflow_content):
        """Get deploy job configuration"""
        return workflow_content['jobs']['deploy']
    
    def test_deploy_job_has_runner(self, deploy_job):
        """Test that deploy job defines a runner"""
        assert 'runs-on' in deploy_job, "Deploy job must specify runner"
        assert deploy_job['runs-on'] == 'ubuntu-latest', "Deploy job should use ubuntu-latest"
    
    def test_deploy_job_depends_on_build(self, deploy_job):
        """Test that deploy job depends on build job"""
        assert 'needs' in deploy_job, "Deploy job should specify dependencies"
        needs = deploy_job['needs']
        if isinstance(needs, str):
            assert needs == 'build', "Deploy job should depend on 'build' job"
        elif isinstance(needs, list):
            assert 'build' in needs, "Deploy job should depend on 'build' job"
    
    def test_deploy_job_has_environment(self, deploy_job):
        """Test that deploy job specifies environment"""
        assert 'environment' in deploy_job, "Deploy job should specify environment"
    
    def test_deploy_environment_is_github_pages(self, deploy_job):
        """Test that deploy job uses github-pages environment"""
        environment = deploy_job['environment']
        if isinstance(environment, dict):
            assert 'name' in environment, "Environment should have a name"
            assert environment['name'] == 'github-pages', "Should deploy to 'github-pages' environment"
        else:
            assert environment == 'github-pages', "Should deploy to 'github-pages' environment"
    
    def test_deploy_environment_has_url(self, deploy_job):
        """Test that deploy environment specifies URL"""
        environment = deploy_job['environment']
        if isinstance(environment, dict):
            assert 'url' in environment, "Environment should specify URL"
            url = environment['url']
            assert '${{' in url and '}}' in url, "URL should use GitHub expressions"
            assert 'deployment.outputs.page_url' in url, "URL should reference deployment output"
    
    def test_deploy_job_has_steps(self, deploy_job):
        """Test that deploy job has steps"""
        assert 'steps' in deploy_job, "Deploy job must have steps"
        steps = deploy_job['steps']
        assert isinstance(steps, list), "Steps must be a list"
        assert len(steps) > 0, "Deploy job must have at least one step"
    
    def test_deploy_job_uses_deploy_pages_action(self, deploy_job):
        """Test that deploy job uses deploy-pages action"""
        steps = deploy_job['steps']
        deploy_steps = [s for s in steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps) > 0, "Deploy job must use deploy-pages action"
    
    def test_deploy_step_has_id(self, deploy_job):
        """Test that deploy step has an ID for output reference"""
        steps = deploy_job['steps']
        deploy_steps = [s for s in steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps) > 0, "Deploy step not found"
        
        deploy_step = deploy_steps[0]
        assert 'id' in deploy_step, "Deploy step should have an ID"
        assert deploy_step['id'] == 'deployment', "Deploy step ID should be 'deployment'"


class TestActionVersions:
    """Test that all actions use proper versions"""
    
    def test_all_actions_are_versioned(self, workflow_content):
        """Test that all actions specify versions"""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    action = step['uses']
                    assert '@' in action, f"Action '{action}' in job '{job_name}' should specify version"
    
    def test_checkout_uses_v4(self, workflow_content):
        """Test that checkout action uses v4"""
        jobs = workflow_content.get('jobs', {})
        for job_config in jobs.values():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step and 'checkout' in step['uses']:
                    assert 'actions/checkout@v4' in step['uses'], \
                        "Checkout action should use v4"
    
    def test_configure_pages_uses_v5(self, workflow_content):
        """Test that configure-pages action uses v5"""
        jobs = workflow_content.get('jobs', {})
        for job_config in jobs.values():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step and 'configure-pages' in step['uses']:
                    assert 'actions/configure-pages@v5' in step['uses'], \
                        "Configure-pages action should use v5"
    
    def test_upload_artifact_uses_v3(self, workflow_content):
        """Test that upload-pages-artifact uses v3"""
        jobs = workflow_content.get('jobs', {})
        for job_config in jobs.values():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step and 'upload-pages-artifact' in step['uses']:
                    assert 'actions/upload-pages-artifact@v3' in step['uses'], \
                        "Upload-pages-artifact should use v3"
    
    def test_deploy_pages_uses_v4(self, workflow_content):
        """Test that deploy-pages uses v4"""
        jobs = workflow_content.get('jobs', {})
        for job_config in jobs.values():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step and 'deploy-pages' in step['uses']:
                    assert 'actions/deploy-pages@v4' in step['uses'], \
                        "Deploy-pages should use v4"


class TestStepNames:
    """Test that steps have descriptive names"""
    
    def test_important_steps_are_named(self, workflow_content):
        """Test that key steps have names for clarity"""
        jobs = workflow_content.get('jobs', {})
        for job_config in jobs.values():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    # Important actions should have names
                    if any(action in step['uses'] for action in 
                           ['checkout', 'configure-pages', 'jekyll-build', 'upload', 'deploy']):
                        assert 'name' in step, \
                            f"Step using '{step['uses']}' should have a descriptive name"


class TestYAMLQuality:
    """Test YAML file quality and formatting"""
    
    def test_no_tabs_in_yaml(self, workflow_raw):
        """Test that workflow uses spaces, not tabs"""
        assert '\t' not in workflow_raw, "YAML should use spaces, not tabs"
    
    def test_consistent_indentation(self, workflow_raw):
        """Test that indentation is consistent (multiples of 2)"""
        lines = workflow_raw.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    assert leading_spaces % 2 == 0, \
                        f"Line {i} has inconsistent indentation"
    
    def test_has_comments(self, workflow_raw):
        """Test that workflow includes documentation comments"""
        comment_lines = [line for line in workflow_raw.split('\n') 
                        if line.strip().startswith('#')]
        assert len(comment_lines) > 0, "Workflow should have documentation comments"


class TestEdgeCases:
    """Test edge cases and failure scenarios"""
    
    def test_no_duplicate_job_names(self, workflow_content):
        """Test that job names are unique"""
        jobs = workflow_content.get('jobs', {})
        job_names = list(jobs.keys())
        assert len(job_names) == len(set(job_names)), "Job names must be unique"
    
    def test_no_duplicate_step_names(self, workflow_content):
        """Test that step names are unique within each job"""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            step_names = [s.get('name') for s in steps if 'name' in s]
            assert len(step_names) == len(set(step_names)), \
                f"Duplicate step names in job '{job_name}'"
    
    def test_runner_is_valid(self, workflow_content):
        """Test that runner specifications are valid"""
        valid_runners = [
            'ubuntu-latest', 'ubuntu-22.04', 'ubuntu-20.04',
            'windows-latest', 'windows-2022', 'windows-2019',
            'macos-latest', 'macos-13', 'macos-12', 'macos-11'
        ]
        
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            runner = job_config.get('runs-on')
            if isinstance(runner, str):
                assert runner in valid_runners, \
                    f"Invalid runner '{runner}' in job '{job_name}'"


class TestSecurityBestPractices:
    """Test security-related configurations"""
    
    def test_no_hardcoded_secrets(self, workflow_raw):
        """Test that workflow doesn't contain hardcoded secrets"""
        suspicious_patterns = ['password', 'token', 'api_key', 'secret']
        lower_content = workflow_raw.lower()
        
        for pattern in suspicious_patterns:
            if pattern in lower_content:
                lines = workflow_raw.split('\n')
                for line in lines:
                    if pattern in line.lower() and not line.strip().startswith('#'):
                        assert 'secrets.' in line or '${{' in line, \
                            f"Potential hardcoded secret pattern '{pattern}' found"
    
    def test_permissions_are_restrictive(self, workflow_content):
        """Test that permissions follow principle of least privilege"""
        permissions = workflow_content.get('permissions', {})
        
        # Should not have write access to contents for deployment workflow
        if 'contents' in permissions:
            assert permissions['contents'] != 'write', \
                "Deployment workflow should not need contents write access"


class TestWorkflowFileLocation:
    """Test workflow file location and naming"""
    
    def test_workflow_in_correct_directory(self, workflow_path):
        """Test that workflow is in .github/workflows"""
        assert '.github' in workflow_path.parts, "Must be in .github directory"
        assert 'workflows' in workflow_path.parts, "Must be in workflows subdirectory"
    
    def test_workflow_has_yml_extension(self, workflow_path):
        """Test that workflow has .yml extension"""
        assert workflow_path.suffix in ['.yml', '.yaml'], \
            "Workflow must have .yml or .yaml extension"
    
    def test_workflow_file_is_readable(self, workflow_path):
        """Test that workflow file is readable"""
        assert os.access(workflow_path, os.R_OK), "Workflow file must be readable"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])