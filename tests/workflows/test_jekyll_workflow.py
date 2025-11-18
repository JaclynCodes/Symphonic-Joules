"""
Comprehensive test suite for .github/workflows/jekyll-gh-pages.yml

This test suite validates the GitHub Actions workflow for Jekyll site deployment including:
- YAML syntax and structure validation
- Workflow metadata and naming
- Trigger configuration (push and workflow_dispatch)
- Permissions configuration for GitHub Pages deployment
- Concurrency control settings
- Job definitions (build and deploy)
- Step configurations and action versions
- Environment configuration
- Security best practices
- Edge cases and failure scenarios
"""

import pytest
import yaml
import os
from pathlib import Path


# Module-level fixtures to cache expensive operations
@pytest.fixture(scope='module')
def workflow_path():
    """
    Module-scoped fixture for workflow file path.
    Computed once and shared across all tests in this module.
    """
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / '.github' / 'workflows' / 'jekyll-gh-pages.yml'


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
    """
    return yaml.safe_load(workflow_raw)


@pytest.fixture(scope='module')
def jobs(workflow_content):
    """
    Module-scoped fixture for jobs configuration.
    Extracted once and shared across all tests.
    """
    return workflow_content.get('jobs', {})


@pytest.fixture(scope='module')
def permissions(workflow_content):
    """
    Module-scoped fixture for permissions configuration.
    """
    return workflow_content.get('permissions', {})


@pytest.fixture(scope='module')
def concurrency(workflow_content):
    """
    Module-scoped fixture for concurrency configuration.
    """
    return workflow_content.get('concurrency', {})


class TestWorkflowStructure:
    """Test the basic structure and syntax of the Jekyll workflow file"""
    
    def test_workflow_file_exists(self, workflow_path):
        """Test that the Jekyll workflow file exists at the expected location"""
        assert workflow_path.exists(), f"Workflow file not found at {workflow_path}"
        assert workflow_path.is_file(), f"Expected file but found directory at {workflow_path}"
    
    def test_workflow_is_valid_yaml(self, workflow_content):
        """Test that the workflow file contains valid YAML"""
        assert workflow_content is not None, "Workflow content is None"
        assert isinstance(workflow_content, dict), "Workflow content must be a dictionary"
        assert len(workflow_content) > 0, "Workflow content is empty"
    
    def test_workflow_has_required_top_level_keys(self, workflow_content):
        """Test that workflow has all required top-level keys"""
        required_keys = ['name', 'jobs']
        for key in required_keys:
            assert key in workflow_content, f"Workflow missing required key '{key}'"
        
        # Check for trigger configuration (parsed as True or 'on')
        assert True in workflow_content or 'on' in workflow_content, \
            "Workflow missing trigger configuration"
    
    def test_workflow_has_permissions_section(self, workflow_content):
        """Test that workflow has permissions configuration for GitHub Pages"""
        assert 'permissions' in workflow_content, \
            "Workflow missing 'permissions' section required for Pages deployment"
    
    def test_workflow_has_concurrency_control(self, workflow_content):
        """Test that workflow has concurrency configuration"""
        assert 'concurrency' in workflow_content, \
            "Workflow missing 'concurrency' section for deployment control"


class TestWorkflowMetadata:
    """Test workflow metadata and naming"""
    
    def test_workflow_name_is_defined(self, workflow_content):
        """Test that workflow has a descriptive name"""
        assert 'name' in workflow_content, "Workflow name not defined"
        name = workflow_content['name']
        assert isinstance(name, str), "Workflow name must be a string"
        assert len(name) > 0, "Workflow name cannot be empty"
    
    def test_workflow_name_mentions_jekyll(self, workflow_content):
        """Test that workflow name mentions Jekyll for clarity"""
        name = workflow_content['name'].lower()
        assert 'jekyll' in name, "Workflow name should mention 'Jekyll' for clarity"
    
    def test_workflow_name_mentions_pages(self, workflow_content):
        """Test that workflow name mentions GitHub Pages"""
        name = workflow_content['name'].lower()
        assert 'pages' in name or 'github pages' in name, \
            "Workflow name should mention 'Pages' or 'GitHub Pages'"


class TestTriggerConfiguration:
    """Test trigger configuration for the workflow"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """Get trigger configuration from workflow content"""
        return workflow_content.get(True) or workflow_content.get('on')
    
    def test_has_trigger_configuration(self, triggers):
        """Test that workflow has trigger configuration"""
        assert triggers is not None, "Workflow has no trigger configuration"
        assert isinstance(triggers, dict), "Trigger configuration must be a dictionary"
    
    def test_has_push_trigger(self, triggers):
        """Test that workflow is triggered on push events"""
        assert 'push' in triggers, "Workflow should be triggered on push events"
    
    def test_push_trigger_targets_main_branch(self, triggers):
        """Test that push trigger targets the main branch"""
        push_config = triggers.get('push')
        assert push_config is not None, "Push trigger configuration is missing"
        assert 'branches' in push_config, "Push trigger missing branches configuration"
        
        branches = push_config['branches']
        assert isinstance(branches, list), "Push branches must be a list"
        assert 'main' in branches, "Push trigger should include 'main' branch"
    
    def test_has_workflow_dispatch(self, triggers):
        """Test that workflow can be manually triggered"""
        assert 'workflow_dispatch' in triggers, \
            "Workflow should support manual triggering via workflow_dispatch"
    
    def test_no_pull_request_trigger(self, triggers):
        """Test that workflow does not trigger on pull requests (deploy only)"""
        assert 'pull_request' not in triggers, \
            "Deploy workflow should not trigger on pull requests"


class TestPermissionsConfiguration:
    """Test permissions configuration for GitHub Pages deployment"""
    
    def test_permissions_section_exists(self, permissions):
        """Test that permissions section is properly configured"""
        assert permissions is not None, "Permissions configuration is missing"
        assert isinstance(permissions, dict), "Permissions must be a dictionary"
        assert len(permissions) > 0, "Permissions section is empty"
    
    def test_has_contents_read_permission(self, permissions):
        """Test that workflow has contents read permission"""
        assert 'contents' in permissions, "Missing 'contents' permission"
        assert permissions['contents'] == 'read', \
            "Contents permission should be 'read'"
    
    def test_has_pages_write_permission(self, permissions):
        """Test that workflow has pages write permission"""
        assert 'pages' in permissions, "Missing 'pages' permission"
        assert permissions['pages'] == 'write', \
            "Pages permission should be 'write' for deployment"
    
    def test_has_id_token_write_permission(self, permissions):
        """Test that workflow has id-token write permission"""
        assert 'id-token' in permissions, "Missing 'id-token' permission"
        assert permissions['id-token'] == 'write', \
            "ID token permission should be 'write' for OIDC authentication"
    
    def test_no_excessive_permissions(self, permissions):
        """Test that workflow follows least privilege principle"""
        allowed_permissions = {'contents', 'pages', 'id-token'}
        actual_permissions = set(permissions.keys())
        
        excessive = actual_permissions - allowed_permissions
        assert len(excessive) == 0, \
            f"Workflow has excessive permissions: {excessive}"


class TestConcurrencyConfiguration:
    """Test concurrency control configuration"""
    
    def test_concurrency_section_exists(self, concurrency):
        """Test that concurrency section is configured"""
        assert concurrency is not None, "Concurrency configuration is missing"
        assert isinstance(concurrency, dict), "Concurrency must be a dictionary"
    
    def test_has_concurrency_group(self, concurrency):
        """Test that concurrency group is defined"""
        assert 'group' in concurrency, "Concurrency group not defined"
        group = concurrency['group']
        assert isinstance(group, str), "Concurrency group must be a string"
        assert len(group) > 0, "Concurrency group cannot be empty"
    
    def test_concurrency_group_is_pages(self, concurrency):
        """Test that concurrency group is set to 'pages'"""
        assert concurrency['group'] == 'pages', \
            "Concurrency group should be 'pages' for Pages deployments"
    
    def test_cancel_in_progress_is_false(self, concurrency):
        """Test that cancel-in-progress is set to false for production deployments"""
        assert 'cancel-in-progress' in concurrency, \
            "Concurrency missing 'cancel-in-progress' setting"
        assert concurrency['cancel-in-progress'] is False, \
            "cancel-in-progress should be False to allow production deployments to complete"


class TestJobsConfiguration:
    """Test jobs configuration"""
    
    def test_jobs_section_exists(self, jobs):
        """Test that jobs section exists and is not empty"""
        assert jobs is not None, "Jobs section is missing"
        assert len(jobs) > 0, "Jobs section is empty"
    
    def test_has_build_job(self, jobs):
        """Test that workflow has a build job"""
        assert 'build' in jobs, "Workflow missing 'build' job"
    
    def test_has_deploy_job(self, jobs):
        """Test that workflow has a deploy job"""
        assert 'deploy' in jobs, "Workflow missing 'deploy' job"
    
    def test_exactly_two_jobs(self, jobs):
        """Test that workflow has exactly two jobs (build and deploy)"""
        assert len(jobs) == 2, \
            f"Expected exactly 2 jobs (build and deploy), got {len(jobs)}"
    
    def test_all_jobs_have_runner(self, jobs):
        """Test that all jobs have runner configuration"""
        for job_name, job_config in jobs.items():
            assert 'runs-on' in job_config, \
                f"Job '{job_name}' missing 'runs-on' configuration"
    
    def test_all_jobs_use_ubuntu_latest(self, jobs):
        """Test that all jobs use ubuntu-latest runner"""
        for job_name, job_config in jobs.items():
            runner = job_config.get('runs-on')
            assert runner == 'ubuntu-latest', \
                f"Job '{job_name}' should use 'ubuntu-latest', got '{runner}'"


class TestBuildJob:
    """Test build job configuration"""
    
    @pytest.fixture
    def build_job(self, jobs):
        """Get build job configuration"""
        return jobs.get('build', {})
    
    def test_build_job_has_steps(self, build_job):
        """Test that build job has steps defined"""
        assert 'steps' in build_job, "Build job missing 'steps'"
        steps = build_job['steps']
        assert isinstance(steps, list), "Build job steps must be a list"
        assert len(steps) > 0, "Build job has no steps"
    
    def test_build_job_has_four_steps(self, build_job):
        """Test that build job has exactly four steps"""
        steps = build_job.get('steps', [])
        assert len(steps) == 4, \
            f"Build job should have 4 steps, got {len(steps)}"
    
    @pytest.fixture
    def build_steps(self, build_job):
        """Get build job steps"""
        return build_job.get('steps', [])
    
    def test_first_step_is_checkout(self, build_steps):
        """Test that first step checks out the repository"""
        first_step = build_steps[0]
        assert 'uses' in first_step, "First step should use an action"
        assert 'checkout' in first_step['uses'].lower(), \
            "First step should be checkout action"
    
    def test_checkout_uses_v4(self, build_steps):
        """Test that checkout action uses version 4"""
        checkout_steps = [s for s in build_steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "No checkout step found"
        assert '@v4' in checkout_steps[0]['uses'], \
            "Checkout action should use version 4"
    
    def test_has_setup_pages_step(self, build_steps):
        """Test that build job includes setup pages action"""
        setup_steps = [s for s in build_steps 
                      if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(setup_steps) > 0, "Build job missing Setup Pages step"
    
    def test_setup_pages_uses_v5(self, build_steps):
        """Test that setup pages action uses version 5"""
        setup_steps = [s for s in build_steps 
                      if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(setup_steps) > 0, "Setup Pages step not found"
        assert '@v5' in setup_steps[0]['uses'], \
            "Setup Pages should use version 5"
    
    def test_has_jekyll_build_step(self, build_steps):
        """Test that build job includes Jekyll build action"""
        jekyll_steps = [s for s in build_steps 
                       if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "Build job missing Jekyll build step"
    
    def test_jekyll_build_uses_v1(self, build_steps):
        """Test that Jekyll build action uses version 1"""
        jekyll_steps = [s for s in build_steps 
                       if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert '@v1' in jekyll_steps[0]['uses'], \
            "Jekyll build should use version 1"
    
    def test_jekyll_build_has_with_parameters(self, build_steps):
        """Test that Jekyll build step has source and destination parameters"""
        jekyll_steps = [s for s in build_steps 
                       if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "Jekyll build step not found"
        
        jekyll_step = jekyll_steps[0]
        assert 'with' in jekyll_step, "Jekyll build step missing 'with' parameters"
        
        with_params = jekyll_step['with']
        assert 'source' in with_params, "Jekyll build missing 'source' parameter"
        assert 'destination' in with_params, "Jekyll build missing 'destination' parameter"
    
    def test_jekyll_source_is_root(self, build_steps):
        """Test that Jekyll source is set to repository root"""
        jekyll_steps = [s for s in build_steps 
                       if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        source = jekyll_steps[0]['with']['source']
        assert source == './', "Jekyll source should be './' (repository root)"
    
    def test_jekyll_destination_is_site(self, build_steps):
        """Test that Jekyll destination is set to _site"""
        jekyll_steps = [s for s in build_steps 
                       if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        destination = jekyll_steps[0]['with']['destination']
        assert destination == './_site', \
            "Jekyll destination should be './_site'"
    
    def test_has_upload_artifact_step(self, build_steps):
        """Test that build job includes upload artifact action"""
        upload_steps = [s for s in build_steps 
                       if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "Build job missing upload artifact step"
    
    def test_upload_artifact_uses_v3(self, build_steps):
        """Test that upload artifact action uses version 3"""
        upload_steps = [s for s in build_steps 
                       if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert '@v3' in upload_steps[0]['uses'], \
            "Upload artifact should use version 3"
    
    def test_all_steps_have_names(self, build_steps):
        """Test that all build steps have descriptive names"""
        for i, step in enumerate(build_steps):
            assert 'name' in step, f"Build step {i} missing 'name' field"
            name = step['name']
            assert isinstance(name, str), f"Build step {i} name must be a string"
            assert len(name) > 0, f"Build step {i} name cannot be empty"


class TestDeployJob:
    """Test deploy job configuration"""
    
    @pytest.fixture
    def deploy_job(self, jobs):
        """Get deploy job configuration"""
        return jobs.get('deploy', {})
    
    def test_deploy_job_has_environment(self, deploy_job):
        """Test that deploy job has environment configuration"""
        assert 'environment' in deploy_job, "Deploy job missing 'environment' configuration"
    
    def test_environment_name_is_github_pages(self, deploy_job):
        """Test that environment name is 'github-pages'"""
        env = deploy_job.get('environment', {})
        assert 'name' in env, "Environment missing 'name' field"
        assert env['name'] == 'github-pages', \
            "Environment name should be 'github-pages'"
    
    def test_environment_has_url(self, deploy_job):
        """Test that environment has URL output"""
        env = deploy_job.get('environment', {})
        assert 'url' in env, "Environment missing 'url' field"
        url = env['url']
        assert isinstance(url, str), "Environment URL must be a string"
        assert '${{' in url and '}}' in url, \
            "Environment URL should reference deployment output"
    
    def test_deploy_job_depends_on_build(self, deploy_job):
        """Test that deploy job depends on build job"""
        assert 'needs' in deploy_job, "Deploy job missing 'needs' dependency"
        needs = deploy_job['needs']
        
        # Can be string or list
        if isinstance(needs, str):
            assert needs == 'build', "Deploy job should depend on 'build' job"
        elif isinstance(needs, list):
            assert 'build' in needs, "Deploy job should depend on 'build' job"
        else:
            pytest.fail("Deploy job 'needs' must be string or list")
    
    def test_deploy_job_has_steps(self, deploy_job):
        """Test that deploy job has steps defined"""
        assert 'steps' in deploy_job, "Deploy job missing 'steps'"
        steps = deploy_job['steps']
        assert isinstance(steps, list), "Deploy job steps must be a list"
        assert len(steps) > 0, "Deploy job has no steps"
    
    @pytest.fixture
    def deploy_steps(self, deploy_job):
        """Get deploy job steps"""
        return deploy_job.get('steps', [])
    
    def test_deploy_has_one_step(self, deploy_steps):
        """Test that deploy job has exactly one step"""
        assert len(deploy_steps) == 1, \
            f"Deploy job should have 1 step, got {len(deploy_steps)}"
    
    def test_deploy_step_is_deploy_pages(self, deploy_steps):
        """Test that deploy step uses deploy-pages action"""
        deploy_step = deploy_steps[0]
        assert 'uses' in deploy_step, "Deploy step should use an action"
        assert 'deploy-pages' in deploy_step['uses'], \
            "Deploy step should use deploy-pages action"
    
    def test_deploy_pages_uses_v4(self, deploy_steps):
        """Test that deploy-pages action uses version 4"""
        deploy_step = deploy_steps[0]
        assert '@v4' in deploy_step['uses'], \
            "Deploy-pages should use version 4"
    
    def test_deploy_step_has_id(self, deploy_steps):
        """Test that deploy step has an ID for output reference"""
        deploy_step = deploy_steps[0]
        assert 'id' in deploy_step, "Deploy step missing 'id' for output reference"
        assert deploy_step['id'] == 'deployment', \
            "Deploy step ID should be 'deployment'"


class TestWorkflowComments:
    """Test comments and documentation in the workflow file"""
    
    def test_has_comments(self, workflow_raw):
        """Test that workflow file contains comments"""
        comment_lines = [line for line in workflow_raw.split('\n') 
                        if line.strip().startswith('#')]
        assert len(comment_lines) > 0, \
            "Workflow should contain comments for documentation"
    
    def test_has_sample_workflow_comment(self, workflow_raw):
        """Test that workflow identifies itself as a sample"""
        assert 'sample' in workflow_raw.lower() or 'Sample' in workflow_raw, \
            "Workflow should identify itself as a sample workflow"
    
    def test_mentions_jekyll_in_comments(self, workflow_raw):
        """Test that comments mention Jekyll"""
        assert 'Jekyll' in workflow_raw or 'jekyll' in workflow_raw, \
            "Comments should mention Jekyll"
    
    def test_mentions_github_pages_in_comments(self, workflow_raw):
        """Test that comments mention GitHub Pages"""
        assert 'GitHub Pages' in workflow_raw or 'Pages' in workflow_raw, \
            "Comments should mention GitHub Pages"


class TestEdgeCases:
    """Test edge cases and potential failure scenarios"""
    
    def test_no_yaml_syntax_errors(self, workflow_content):
        """Test that YAML is syntactically valid"""
        assert workflow_content is not None, "YAML content should be loaded"
    
    def test_no_tabs_in_yaml(self, workflow_raw):
        """Test that workflow uses spaces, not tabs"""
        assert '\t' not in workflow_raw, "YAML file should use spaces, not tabs"
    
    def test_consistent_indentation(self, workflow_raw):
        """Test that indentation is consistent (multiples of 2)"""
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
    
    def test_no_duplicate_step_names_in_jobs(self, jobs):
        """Test that there are no duplicate step names within jobs"""
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            step_names = [s.get('name') for s in steps if 'name' in s]
            assert len(step_names) == len(set(step_names)), \
                f"Duplicate step names in job '{job_name}'"
    
    def test_all_actions_are_versioned(self, jobs):
        """Test that all actions use version tags (security best practice)"""
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    action = step['uses']
                    assert '@' in action, \
                        f"Action '{action}' in job '{job_name}' should specify a version"


class TestWorkflowSecurity:
    """Test security aspects of the workflow"""
    
    def test_no_hardcoded_secrets(self, workflow_raw):
        """Test that workflow doesn't contain hardcoded secrets"""
        suspicious_patterns = ['password', 'api_key', 'secret']
        lower_content = workflow_raw.lower()
        
        for pattern in suspicious_patterns:
            if pattern in lower_content:
                lines = workflow_raw.split('\n')
                for line in lines:
                    if pattern in line.lower() and not line.strip().startswith('#'):
                        # Check if it's using GitHub secrets context
                        assert 'secrets.' in line or '${{' in line, \
                            f"Potential hardcoded secret pattern '{pattern}' found"
    
    def test_uses_oidc_authentication(self, permissions):
        """Test that workflow uses OIDC for authentication"""
        assert 'id-token' in permissions, \
            "Workflow should use OIDC (id-token permission) for secure authentication"
        assert permissions['id-token'] == 'write', \
            "id-token permission should be 'write' for OIDC"
    
    def test_minimal_permissions(self, permissions):
        """Test that workflow uses minimal required permissions"""
        # Should only have contents:read, pages:write, id-token:write
        assert len(permissions) == 3, \
            f"Workflow should have exactly 3 permissions, got {len(permissions)}"


class TestWorkflowFilePermissions:
    """Test file permissions and location"""
    
    def test_workflow_in_correct_directory(self, workflow_path):
        """Test that workflow is in .github/workflows directory"""
        assert '.github' in workflow_path.parts, \
            "Workflow must be in .github directory"
        assert 'workflows' in workflow_path.parts, \
            "Workflow must be in workflows subdirectory"
    
    def test_workflow_has_yml_extension(self, workflow_path):
        """Test that workflow file has .yml extension"""
        assert workflow_path.suffix == '.yml', \
            "Workflow file should have .yml extension"
    
    def test_workflow_file_is_readable(self, workflow_path):
        """Test that workflow file is readable"""
        assert os.access(workflow_path, os.R_OK), \
            "Workflow file must be readable"


class TestJobDependencies:
    """Test job dependency chain"""
    
    def test_deploy_depends_only_on_build(self, jobs):
        """Test that deploy job depends only on build job"""
        deploy_job = jobs.get('deploy', {})
        needs = deploy_job.get('needs')
        
        if isinstance(needs, str):
            assert needs == 'build', \
                "Deploy should depend only on build job"
        elif isinstance(needs, list):
            assert len(needs) == 1, \
                "Deploy should depend on exactly one job"
            assert needs[0] == 'build', \
                "Deploy should depend on build job"
    
    def test_build_has_no_dependencies(self, jobs):
        """Test that build job has no dependencies"""
        build_job = jobs.get('build', {})
        assert 'needs' not in build_job, \
            "Build job should not have dependencies"


class TestStepNaming:
    """Test step naming conventions"""
    
    def test_build_steps_have_descriptive_names(self, jobs):
        """Test that build steps have descriptive names"""
        build_steps = jobs['build']['steps']
        step_names = [s.get('name', '') for s in build_steps]
        
        # Check for descriptive keywords
        all_names = ' '.join(step_names).lower()
        assert 'checkout' in all_names, "Should have checkout step"
        assert 'setup' in all_names or 'pages' in all_names, \
            "Should have setup/pages step"
        assert 'build' in all_names or 'jekyll' in all_names, \
            "Should have build/jekyll step"
        assert 'upload' in all_names or 'artifact' in all_names, \
            "Should have upload/artifact step"
    
    def test_deploy_step_has_descriptive_name(self, jobs):
        """Test that deploy step has descriptive name"""
        deploy_steps = jobs['deploy']['steps']
        deploy_step = deploy_steps[0]
        
        name = deploy_step.get('name', '').lower()
        assert 'deploy' in name, "Deploy step should mention 'deploy' in name"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])