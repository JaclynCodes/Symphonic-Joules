"""
Comprehensive test suite for .github/workflows/jekyll-gh-pages.yml

This test suite validates the GitHub Actions Jekyll deployment workflow including:
- YAML syntax and structure
- Workflow metadata (name, triggers)
- GitHub Pages permissions configuration
- Concurrency control
- Build and deployment job definitions
- Jekyll-specific actions and configurations
- Security best practices
"""

import pytest
import yaml
from pathlib import Path
from .conftest import check_for_hardcoded_secrets


@pytest.fixture(scope='module')
def workflow_path():
    """Module-scoped fixture for Jekyll workflow file path."""
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


@pytest.fixture(scope='module')
def jobs(workflow_content):
    """Module-scoped fixture for jobs configuration."""
    return workflow_content.get('jobs', {})


class TestWorkflowStructure:
    """Test the basic structure and syntax of the Jekyll workflow"""
    
    def test_workflow_file_exists(self, workflow_path):
        """Test that the Jekyll workflow file exists"""
        assert workflow_path.exists(), f"Jekyll workflow not found at {workflow_path}"
        assert workflow_path.is_file(), "Expected file but found directory"
    
    def test_workflow_is_valid_yaml(self, workflow_content):
        """Test that the workflow is valid YAML"""
        assert workflow_content is not None, "Workflow content is None"
        assert isinstance(workflow_content, dict), "Workflow should be a dictionary"
    
    def test_workflow_has_required_keys(self, workflow_content):
        """Test that workflow has all required top-level keys"""
        required_keys = ['name', 'jobs']
        for key in required_keys:
            assert key in workflow_content, f"Workflow missing '{key}' key"
        
        # Check for trigger configuration
        assert True in workflow_content or 'on' in workflow_content, \
            "Workflow missing trigger configuration"
    
    def test_workflow_has_permissions_section(self, workflow_content):
        """Test that workflow defines permissions for GitHub Pages"""
        assert 'permissions' in workflow_content, \
            "Jekyll workflow should define permissions for Pages deployment"
    
    def test_workflow_has_concurrency_control(self, workflow_content):
        """Test that workflow has concurrency configuration"""
        assert 'concurrency' in workflow_content, \
            "Jekyll workflow should have concurrency control for production deployments"


class TestWorkflowMetadata:
    """Test workflow metadata and naming"""
    
    def test_workflow_name_exists(self, workflow_content):
        """Test that workflow has a name"""
        assert 'name' in workflow_content, "Workflow name not defined"
        assert isinstance(workflow_content['name'], str), "Workflow name must be a string"
        assert len(workflow_content['name']) > 0, "Workflow name cannot be empty"
    
    def test_workflow_name_mentions_jekyll(self, workflow_content):
        """Test that workflow name mentions Jekyll"""
        name = workflow_content['name'].lower()
        assert 'jekyll' in name, "Workflow name should mention Jekyll"
    
    def test_workflow_name_mentions_github_pages(self, workflow_content):
        """Test that workflow name mentions GitHub Pages"""
        name = workflow_content['name'].lower()
        assert 'github pages' in name or 'pages' in name, \
            "Workflow name should mention GitHub Pages"


class TestTriggerConfiguration:
    """Test workflow trigger configuration"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """Get trigger configuration"""
        return workflow_content.get(True) or workflow_content.get('on')
    
    def test_has_push_trigger(self, triggers):
        """Test that workflow triggers on push"""
        assert 'push' in triggers, "Workflow should trigger on push events"
    
    def test_push_trigger_targets_main_branch(self, triggers):
        """Test that push trigger targets main branch"""
        push_config = triggers.get('push', {})
        assert 'branches' in push_config, "Push trigger should specify branches"
        branches = push_config['branches']
        assert isinstance(branches, list), "Branches should be a list"
        assert 'main' in branches, "Push trigger should target 'main' branch"
    
    def test_has_workflow_dispatch(self, triggers):
        """Test that workflow can be manually triggered"""
        assert 'workflow_dispatch' in triggers, \
            "Workflow should support manual triggering via workflow_dispatch"
    
    def test_no_pull_request_trigger(self, triggers):
        """Test that workflow doesn't trigger on pull requests"""
        assert 'pull_request' not in triggers, \
            "Jekyll deployment should not trigger on pull requests (production only)"


class TestPermissionsConfiguration:
    """Test GitHub token permissions configuration"""
    
    @pytest.fixture
    def permissions(self, workflow_content):
        """Get permissions configuration"""
        return workflow_content.get('permissions', {})
    
    def test_permissions_are_defined(self, permissions):
        """Test that permissions are explicitly defined"""
        assert len(permissions) > 0, "Permissions should be explicitly defined"
    
    def test_has_contents_read_permission(self, permissions):
        """Test that workflow has contents read permission"""
        assert 'contents' in permissions, "Should define contents permission"
        assert permissions['contents'] == 'read', \
            "Should have read-only access to repository contents"
    
    def test_has_pages_write_permission(self, permissions):
        """Test that workflow has pages write permission"""
        assert 'pages' in permissions, "Should define pages permission"
        assert permissions['pages'] == 'write', \
            "Should have write access to GitHub Pages"
    
    def test_has_id_token_write_permission(self, permissions):
        """Test that workflow has id-token write permission for OIDC"""
        assert 'id-token' in permissions, "Should define id-token permission"
        assert permissions['id-token'] == 'write', \
            "Should have write access to id-token for OIDC authentication"
    
    def test_follows_least_privilege_principle(self, permissions):
        """Test that only necessary permissions are granted"""
        allowed_permissions = {'contents', 'pages', 'id-token'}
        granted_permissions = set(permissions.keys())
        extra_permissions = granted_permissions - allowed_permissions
        assert len(extra_permissions) == 0, \
            f"Unnecessary permissions granted: {extra_permissions}"


class TestConcurrencyConfiguration:
    """Test concurrency control configuration"""
    
    @pytest.fixture
    def concurrency(self, workflow_content):
        """Get concurrency configuration"""
        return workflow_content.get('concurrency', {})
    
    def test_concurrency_group_is_defined(self, concurrency):
        """Test that concurrency group is defined"""
        assert 'group' in concurrency, "Concurrency group should be defined"
        assert isinstance(concurrency['group'], str), "Concurrency group must be a string"
        assert len(concurrency['group']) > 0, "Concurrency group cannot be empty"
    
    def test_concurrency_group_is_pages(self, concurrency):
        """Test that concurrency group is 'pages'"""
        assert concurrency['group'] == 'pages', \
            "Concurrency group should be 'pages' for GitHub Pages deployments"
    
    def test_cancel_in_progress_is_false(self, concurrency):
        """Test that cancel-in-progress is false for production deployments"""
        assert 'cancel-in-progress' in concurrency, \
            "cancel-in-progress should be explicitly set"
        assert concurrency['cancel-in-progress'] is False, \
            "Should not cancel in-progress deployments (production safety)"


class TestJobsConfiguration:
    """Test jobs configuration"""
    
    def test_has_build_job(self, jobs):
        """Test that workflow has a build job"""
        assert 'build' in jobs, "Workflow should have a 'build' job"
    
    def test_has_deploy_job(self, jobs):
        """Test that workflow has a deploy job"""
        assert 'deploy' in jobs, "Workflow should have a 'deploy' job"
    
    def test_jobs_count(self, jobs):
        """Test that workflow has exactly 2 jobs (build and deploy)"""
        assert len(jobs) == 2, f"Expected 2 jobs (build, deploy), got {len(jobs)}"
    
    def test_all_jobs_have_runner(self, jobs):
        """Test that all jobs specify a runner"""
        for job_name, job_config in jobs.items():
            assert 'runs-on' in job_config, \
                f"Job '{job_name}' should specify runs-on"
    
    def test_all_jobs_use_ubuntu_latest(self, jobs):
        """Test that all jobs use ubuntu-latest runner"""
        for job_name, job_config in jobs.items():
            runner = job_config.get('runs-on')
            assert runner == 'ubuntu-latest', \
                f"Job '{job_name}' should use ubuntu-latest, got '{runner}'"


class TestBuildJob:
    """Test the build job configuration"""
    
    @pytest.fixture
    def build_job(self, jobs):
        """Get build job configuration"""
        return jobs.get('build', {})
    
    @pytest.fixture
    def build_steps(self, build_job):
        """Get build job steps"""
        return build_job.get('steps', [])
    
    def test_build_job_has_steps(self, build_job):
        """Test that build job has steps"""
        assert 'steps' in build_job, "Build job should have steps"
        assert isinstance(build_job['steps'], list), "Steps should be a list"
        assert len(build_job['steps']) > 0, "Build job should have at least one step"
    
    def test_has_checkout_step(self, build_steps):
        """Test that build job checks out repository"""
        checkout_steps = [s for s in build_steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "Build job should checkout repository"
    
    def test_checkout_uses_v4(self, build_steps):
        """Test that checkout action uses v4"""
        checkout_steps = [s for s in build_steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "No checkout step found"
        assert 'actions/checkout@v4' in checkout_steps[0]['uses'], \
            "Checkout should use v4"
    
    def test_has_setup_pages_step(self, build_steps):
        """Test that build job sets up GitHub Pages"""
        setup_steps = [s for s in build_steps if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(setup_steps) > 0, "Build job should configure GitHub Pages"
    
    def test_setup_pages_uses_v5(self, build_steps):
        """Test that configure-pages action uses v5"""
        setup_steps = [s for s in build_steps if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(setup_steps) > 0, "No setup pages step found"
        assert 'actions/configure-pages@v5' in setup_steps[0]['uses'], \
            "Configure-pages should use v5"
    
    def test_has_jekyll_build_step(self, build_steps):
        """Test that build job builds with Jekyll"""
        jekyll_steps = [s for s in build_steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "Build job should build with Jekyll"
    
    def test_jekyll_build_uses_v1(self, build_steps):
        """Test that jekyll-build-pages action uses v1"""
        jekyll_steps = [s for s in build_steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "No Jekyll build step found"
        assert 'actions/jekyll-build-pages@v1' in jekyll_steps[0]['uses'], \
            "Jekyll-build-pages should use v1"
    
    def test_jekyll_build_has_with_parameters(self, build_steps):
        """Test that Jekyll build step has with parameters"""
        jekyll_steps = [s for s in build_steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "No Jekyll build step found"
        assert 'with' in jekyll_steps[0], "Jekyll build should have 'with' parameters"
    
    def test_jekyll_build_specifies_source(self, build_steps):
        """Test that Jekyll build specifies source directory"""
        jekyll_steps = [s for s in build_steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        with_params = jekyll_steps[0].get('with', {})
        assert 'source' in with_params, "Jekyll build should specify source"
        assert with_params['source'] == './', "Source should be repository root"
    
    def test_jekyll_build_specifies_destination(self, build_steps):
        """Test that Jekyll build specifies destination directory"""
        jekyll_steps = [s for s in build_steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        with_params = jekyll_steps[0].get('with', {})
        assert 'destination' in with_params, "Jekyll build should specify destination"
        assert with_params['destination'] == './_site', "Destination should be _site"
    
    def test_has_upload_artifact_step(self, build_steps):
        """Test that build job uploads artifact"""
        upload_steps = [s for s in build_steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "Build job should upload pages artifact"
    
    def test_upload_artifact_uses_v3(self, build_steps):
        """Test that upload-pages-artifact action uses v3"""
        upload_steps = [s for s in build_steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "No upload artifact step found"
        assert 'actions/upload-pages-artifact@v3' in upload_steps[0]['uses'], \
            "Upload-pages-artifact should use v3"
    
    def test_build_steps_are_in_correct_order(self, build_steps):
        """Test that build steps are in correct order"""
        step_names = []
        for step in build_steps:
            if 'uses' in step:
                if 'checkout' in step['uses']:
                    step_names.append('checkout')
                elif 'configure-pages' in step['uses']:
                    step_names.append('setup')
                elif 'jekyll-build-pages' in step['uses']:
                    step_names.append('build')
                elif 'upload-pages-artifact' in step['uses']:
                    step_names.append('upload')
        
        expected_order = ['checkout', 'setup', 'build', 'upload']
        assert step_names == expected_order, \
            f"Steps should be in order: {expected_order}, got: {step_names}"


class TestDeployJob:
    """Test the deploy job configuration"""
    
    @pytest.fixture
    def deploy_job(self, jobs):
        """Get deploy job configuration"""
        return jobs.get('deploy', {})
    
    @pytest.fixture
    def deploy_steps(self, deploy_job):
        """Get deploy job steps"""
        return deploy_job.get('steps', [])
    
    def test_deploy_job_has_environment(self, deploy_job):
        """Test that deploy job specifies environment"""
        assert 'environment' in deploy_job, "Deploy job should specify environment"
    
    def test_deploy_environment_is_github_pages(self, deploy_job):
        """Test that deploy environment is github-pages"""
        env = deploy_job.get('environment', {})
        if isinstance(env, dict):
            assert env.get('name') == 'github-pages', \
                "Deploy environment should be 'github-pages'"
        else:
            assert env == 'github-pages', "Deploy environment should be 'github-pages'"
    
    def test_deploy_environment_has_url(self, deploy_job):
        """Test that deploy environment specifies URL"""
        env = deploy_job.get('environment', {})
        if isinstance(env, dict):
            assert 'url' in env, "Deploy environment should specify URL"
            assert '${{ steps.deployment.outputs.page_url }}' in env['url'], \
                "Deploy URL should reference deployment output"
    
    def test_deploy_job_depends_on_build(self, deploy_job):
        """Test that deploy job depends on build job"""
        assert 'needs' in deploy_job, "Deploy job should have dependencies"
        needs = deploy_job['needs']
        if isinstance(needs, list):
            assert 'build' in needs, "Deploy job should depend on build job"
        else:
            assert needs == 'build', "Deploy job should depend on build job"
    
    def test_deploy_job_has_steps(self, deploy_job):
        """Test that deploy job has steps"""
        assert 'steps' in deploy_job, "Deploy job should have steps"
        assert isinstance(deploy_job['steps'], list), "Steps should be a list"
        assert len(deploy_job['steps']) > 0, "Deploy job should have at least one step"
    
    def test_has_deploy_pages_step(self, deploy_steps):
        """Test that deploy job deploys pages"""
        deploy_steps_list = [s for s in deploy_steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps_list) > 0, "Deploy job should deploy pages"
    
    def test_deploy_pages_uses_v4(self, deploy_steps):
        """Test that deploy-pages action uses v4"""
        deploy_steps_list = [s for s in deploy_steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps_list) > 0, "No deploy pages step found"
        assert 'actions/deploy-pages@v4' in deploy_steps_list[0]['uses'], \
            "Deploy-pages should use v4"
    
    def test_deploy_step_has_id(self, deploy_steps):
        """Test that deploy step has ID for output reference"""
        deploy_steps_list = [s for s in deploy_steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps_list) > 0, "No deploy pages step found"
        assert 'id' in deploy_steps_list[0], "Deploy step should have ID"
        assert deploy_steps_list[0]['id'] == 'deployment', \
            "Deploy step ID should be 'deployment'"


class TestWorkflowSecurity:
    """Test security aspects of the Jekyll workflow"""
    
    def test_all_actions_are_versioned(self, jobs):
        """Test that all actions use version tags"""
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    action = step['uses']
                    assert '@' in action, \
                        f"Action '{action}' in job '{job_name}' should specify version"
    
    def test_uses_oidc_authentication(self, workflow_content):
        """Test that workflow uses OIDC for authentication"""
        permissions = workflow_content.get('permissions', {})
        assert 'id-token' in permissions, \
            "Should use OIDC authentication (id-token permission)"
        assert permissions['id-token'] == 'write', \
            "Should have write access to id-token for OIDC"
    
    def test_no_hardcoded_secrets(self, workflow_raw):
        """Test that workflow doesn't contain hardcoded secrets"""
        check_for_hardcoded_secrets(workflow_raw)


class TestEdgeCases:
    """Test edge cases and formatting"""
    
    def test_no_tabs_in_yaml(self, workflow_raw):
        """Test that workflow uses spaces, not tabs"""
        assert '\t' not in workflow_raw, "YAML should use spaces, not tabs"
    
    def test_consistent_indentation(self, workflow_raw):
        """Test that indentation is consistent"""
        lines = workflow_raw.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    assert leading_spaces % 2 == 0, \
                        f"Line {i} has inconsistent indentation"
    
    def test_no_duplicate_job_names(self, jobs):
        """Test that there are no duplicate job names"""
        job_names = list(jobs.keys())
        assert len(job_names) == len(set(job_names)), "Duplicate job names found"
    
    def test_no_duplicate_step_ids(self, jobs):
        """Test that step IDs are unique within each job"""
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            step_ids = [s.get('id') for s in steps if 'id' in s]
            assert len(step_ids) == len(set(step_ids)), \
                f"Duplicate step IDs in job '{job_name}'"


class TestWorkflowComments:
    """Test workflow documentation"""
    
    def test_has_comments(self, workflow_raw):
        """Test that workflow contains comments"""
        comment_lines = [line for line in workflow_raw.split('\n') 
                        if line.strip().startswith('#')]
        assert len(comment_lines) > 0, "Workflow should contain documentation comments"
    
    def test_mentions_jekyll_in_content(self, workflow_raw):
        """Test that workflow mentions Jekyll"""
        assert 'jekyll' in workflow_raw.lower() or 'Jekyll' in workflow_raw, \
            "Workflow should mention Jekyll"
    
    def test_mentions_github_pages(self, workflow_raw):
        """Test that workflow mentions GitHub Pages"""
        assert 'github pages' in workflow_raw.lower() or 'Pages' in workflow_raw, \
            "Workflow should mention GitHub Pages"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])