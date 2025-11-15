"""
Comprehensive test suite for .github/workflows/static.yml

This test suite validates the Static Pages deployment workflow including:
- YAML syntax and structure
- Workflow metadata and naming
- Branch triggers and manual dispatch
- Permissions configuration for GitHub Pages
- Concurrency settings
- Deploy job configuration
- Static content-specific actions and versions
- Upload artifact path configuration
- Environment configuration
- Edge cases and security considerations
"""

import pytest
import yaml
import os
from pathlib import Path


# Module-level fixtures to cache expensive file I/O and parsing operations
@pytest.fixture(scope='module')
def workflow_path():
    """
    Module-scoped fixture for static workflow file path.
    Computed once and shared across all tests in this module.
    """
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / '.github' / 'workflows' / 'static.yml'


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
    """Test the basic structure and syntax of the static workflow file"""
    
    def test_workflow_file_exists(self, workflow_path):
        """Test that the static workflow file exists at the expected location"""
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
        assert True in workflow_content or 'on' in workflow_content, "Workflow missing trigger configuration"


class TestWorkflowMetadata:
    """Test workflow metadata and configuration"""
    
    def test_workflow_name_is_defined(self, workflow_content):
        """Test that workflow has a name defined"""
        assert 'name' in workflow_content, "Workflow name not defined"
        assert isinstance(workflow_content['name'], str), "Workflow name must be a string"
        assert len(workflow_content['name']) > 0, "Workflow name cannot be empty"
    
    def test_workflow_name_mentions_static(self, workflow_content):
        """Test that the workflow name mentions static content"""
        name = workflow_content['name'].lower()
        assert 'static' in name, f"Expected workflow name to mention 'static', got '{workflow_content['name']}'"
    
    def test_workflow_name_mentions_pages(self, workflow_content):
        """Test that the workflow name mentions Pages"""
        name = workflow_content['name'].lower()
        assert 'pages' in name, f"Expected workflow name to mention 'Pages', got '{workflow_content['name']}'"
    
    def test_workflow_has_triggers(self, workflow_content):
        """Test that workflow has trigger configuration"""
        triggers = workflow_content.get(True) or workflow_content.get('on')
        assert triggers is not None, "Workflow has no trigger configuration"


class TestTriggerConfiguration:
    """Test workflow trigger configuration"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """Get trigger configuration from cached workflow content"""
        return workflow_content.get(True) or workflow_content.get('on')
    
    def test_push_trigger_exists(self, triggers):
        """Test that push trigger is configured"""
        assert 'push' in triggers, "Push trigger not configured"
    
    def test_workflow_dispatch_trigger_exists(self, triggers):
        """Test that workflow_dispatch trigger is configured for manual runs"""
        assert 'workflow_dispatch' in triggers, "Workflow dispatch trigger not configured"
    
    def test_push_trigger_targets_main_branch(self, triggers):
        """Test that push trigger targets main branch"""
        push_config = triggers.get('push')
        assert push_config is not None, "Push trigger configuration is None"
        assert 'branches' in push_config, "Push trigger missing branches configuration"
        
        branches = push_config['branches']
        assert isinstance(branches, list), "Push branches must be a list"
        assert 'main' in branches, "Push trigger must include 'main' branch"
    
    def test_no_pull_request_trigger(self, triggers):
        """Test that workflow doesn't trigger on pull requests (deployment workflow)"""
        assert 'pull_request' not in triggers, \
            "Deployment workflow should not trigger on pull requests"


class TestPermissionsConfiguration:
    """Test GitHub Pages permissions configuration"""
    
    def test_permissions_are_defined(self, workflow_content):
        """Test that permissions are explicitly defined"""
        assert 'permissions' in workflow_content, "Permissions not defined"
    
    def test_permissions_is_dict(self, workflow_content):
        """Test that permissions is a dictionary"""
        permissions = workflow_content.get('permissions')
        assert isinstance(permissions, dict), "Permissions must be a dictionary"
    
    def test_contents_read_permission(self, workflow_content):
        """Test that contents read permission is set"""
        permissions = workflow_content['permissions']
        assert 'contents' in permissions, "Missing 'contents' permission"
        assert permissions['contents'] == 'read', \
            f"Expected contents: read, got contents: {permissions['contents']}"
    
    def test_pages_write_permission(self, workflow_content):
        """Test that pages write permission is set for deployment"""
        permissions = workflow_content['permissions']
        assert 'pages' in permissions, "Missing 'pages' permission"
        assert permissions['pages'] == 'write', \
            f"Expected pages: write, got pages: {permissions['pages']}"
    
    def test_id_token_write_permission(self, workflow_content):
        """Test that id-token write permission is set for OIDC"""
        permissions = workflow_content['permissions']
        assert 'id-token' in permissions, "Missing 'id-token' permission"
        assert permissions['id-token'] == 'write', \
            f"Expected id-token: write, got id-token: {permissions['id-token']}"
    
    def test_no_excessive_permissions(self, workflow_content):
        """Test that workflow doesn't request excessive permissions"""
        permissions = workflow_content['permissions']
        allowed_permissions = {'contents', 'pages', 'id-token'}
        excessive = set(permissions.keys()) - allowed_permissions
        assert len(excessive) == 0, f"Excessive permissions requested: {excessive}"


class TestConcurrencyConfiguration:
    """Test concurrency configuration for deployments"""
    
    def test_concurrency_is_defined(self, workflow_content):
        """Test that concurrency control is defined"""
        assert 'concurrency' in workflow_content, "Concurrency configuration not defined"
    
    def test_concurrency_group_is_pages(self, workflow_content):
        """Test that concurrency group is set to 'pages'"""
        concurrency = workflow_content.get('concurrency')
        assert isinstance(concurrency, dict), "Concurrency must be a dictionary"
        assert 'group' in concurrency, "Concurrency group not defined"
        assert concurrency['group'] == 'pages', \
            f"Expected concurrency group 'pages', got '{concurrency['group']}'"
    
    def test_cancel_in_progress_is_false(self, workflow_content):
        """Test that cancel-in-progress is false to allow deployments to complete"""
        concurrency = workflow_content['concurrency']
        assert 'cancel-in-progress' in concurrency, "cancel-in-progress not defined"
        assert concurrency['cancel-in-progress'] is False, \
            "cancel-in-progress should be false for deployment workflows"


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
    
    def test_deploy_job_exists(self, jobs):
        """Test that 'deploy' job is defined"""
        assert 'deploy' in jobs, "Deploy job not defined"
    
    def test_single_job_workflow(self, jobs):
        """Test that workflow has exactly one job (deploy only, no separate build)"""
        assert len(jobs) == 1, f"Expected 1 job (deploy), got {len(jobs)}"
        assert 'deploy' in jobs, "Expected job named 'deploy'"
    
    def test_deploy_job_uses_ubuntu_latest(self, jobs):
        """Test that deploy job uses ubuntu-latest runner"""
        deploy_job = jobs.get('deploy', {})
        assert 'runs-on' in deploy_job, "Deploy job missing 'runs-on' configuration"
        runner = deploy_job['runs-on']
        assert runner == 'ubuntu-latest', f"Expected 'ubuntu-latest' runner, got '{runner}'"


class TestDeployJobConfiguration:
    """Test deploy job specific configuration"""
    
    @pytest.fixture
    def deploy_job(self, workflow_content):
        """Get deploy job configuration"""
        return workflow_content['jobs']['deploy']
    
    def test_deploy_job_has_environment(self, deploy_job):
        """Test that deploy job has environment configuration"""
        assert 'environment' in deploy_job, "Deploy job missing 'environment' configuration"
    
    def test_deploy_environment_is_github_pages(self, deploy_job):
        """Test that deploy environment is github-pages"""
        env = deploy_job.get('environment')
        assert isinstance(env, dict), "Environment must be a dictionary"
        assert 'name' in env, "Environment missing 'name'"
        assert env['name'] == 'github-pages', \
            f"Expected environment 'github-pages', got '{env['name']}'"
    
    def test_deploy_environment_has_url(self, deploy_job):
        """Test that deploy environment has URL configuration"""
        env = deploy_job['environment']
        assert 'url' in env, "Environment missing 'url'"
        assert '${{' in env['url'], "Environment URL should use expression syntax"
        assert 'steps.deployment.outputs.page_url' in env['url'], \
            "Environment URL should reference deployment output"
    
    def test_deploy_job_has_no_needs(self, deploy_job):
        """Test that deploy job has no dependencies (single-job workflow)"""
        assert 'needs' not in deploy_job, \
            "Deploy job should not have 'needs' dependency in single-job workflow"
    
    def test_deploy_job_has_steps(self, deploy_job):
        """Test that deploy job has steps defined"""
        assert 'steps' in deploy_job, "Deploy job missing 'steps'"
        assert isinstance(deploy_job['steps'], list), "Steps must be a list"
        assert len(deploy_job['steps']) > 0, "Deploy job has no steps"
    
    def test_deploy_has_minimum_four_steps(self, deploy_job):
        """Test that deploy job has at least 4 steps"""
        steps = deploy_job['steps']
        assert len(steps) >= 4, f"Expected at least 4 steps in deploy job, got {len(steps)}"
    
    def test_deploy_has_checkout_step(self, deploy_job):
        """Test that deploy job includes checkout action"""
        steps = deploy_job['steps']
        checkout_steps = [s for s in steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "No checkout step found in deploy job"
    
    def test_deploy_has_setup_pages_step(self, deploy_job):
        """Test that deploy job includes setup pages action"""
        steps = deploy_job['steps']
        setup_steps = [s for s in steps if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(setup_steps) > 0, "No setup pages step found in deploy job"
    
    def test_deploy_has_upload_artifact_step(self, deploy_job):
        """Test that deploy job uploads artifact"""
        steps = deploy_job['steps']
        upload_steps = [s for s in steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "No upload artifact step found in deploy job"
    
    def test_deploy_has_deploy_pages_step(self, deploy_job):
        """Test that deploy job includes deploy pages action"""
        steps = deploy_job['steps']
        deploy_steps = [s for s in steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps) > 0, "No deploy pages step found in deploy job"
    
    def test_upload_artifact_has_path_config(self, deploy_job):
        """Test that upload artifact step has path configuration"""
        steps = deploy_job['steps']
        upload_steps = [s for s in steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "No upload artifact step found"
        
        upload_step = upload_steps[0]
        assert 'with' in upload_step, "Upload artifact step missing 'with' configuration"
        assert 'path' in upload_step['with'], "Upload artifact step missing 'path' parameter"
    
    def test_upload_artifact_path_is_current_directory(self, deploy_job):
        """Test that upload artifact path uploads current directory"""
        steps = deploy_job['steps']
        upload_steps = [s for s in steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        upload_step = upload_steps[0]
        
        path = upload_step['with']['path']
        assert path == '.', f"Expected upload path '.', got '{path}'"
    
    def test_deploy_step_has_id(self, deploy_job):
        """Test that deploy step has an id for output reference"""
        steps = deploy_job['steps']
        deploy_steps = [s for s in steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps) > 0, "No deploy pages step found"
        
        deploy_step = deploy_steps[0]
        assert 'id' in deploy_step, "Deploy step missing 'id'"
        assert deploy_step['id'] == 'deployment', \
            f"Expected deploy step id 'deployment', got '{deploy_step['id']}'"


class TestActionVersions:
    """Test that all actions use appropriate versions"""
    
    @pytest.fixture
    def all_steps(self, workflow_content):
        """Get all steps from all jobs"""
        jobs = workflow_content.get('jobs', {})
        all_steps = []
        for job_config in jobs.values():
            all_steps.extend(job_config.get('steps', []))
        return all_steps
    
    def test_all_actions_have_versions(self, all_steps):
        """Test that all action uses specify versions"""
        for step in all_steps:
            if 'uses' in step:
                action = step['uses']
                assert '@' in action, f"Action '{action}' should specify a version"
    
    def test_checkout_uses_v4(self, all_steps):
        """Test that checkout action uses version 4"""
        checkout_steps = [s for s in all_steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "No checkout step found"
        
        for step in checkout_steps:
            action = step['uses']
            assert 'actions/checkout@v4' in action, f"Expected checkout@v4, got {action}"
    
    def test_configure_pages_uses_v5(self, all_steps):
        """Test that configure-pages action uses version 5"""
        config_steps = [s for s in all_steps if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(config_steps) > 0, "No configure-pages step found"
        
        for step in config_steps:
            action = step['uses']
            assert 'actions/configure-pages@v5' in action, \
                f"Expected configure-pages@v5, got {action}"
    
    def test_upload_artifact_uses_v3(self, all_steps):
        """Test that upload-pages-artifact action uses version 3"""
        upload_steps = [s for s in all_steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "No upload-pages-artifact step found"
        
        for step in upload_steps:
            action = step['uses']
            assert 'actions/upload-pages-artifact@v3' in action, \
                f"Expected upload-pages-artifact@v3, got {action}"
    
    def test_deploy_pages_uses_v4(self, all_steps):
        """Test that deploy-pages action uses version 4"""
        deploy_steps = [s for s in all_steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps) > 0, "No deploy-pages step found"
        
        for step in deploy_steps:
            action = step['uses']
            assert 'actions/deploy-pages@v4' in action, \
                f"Expected deploy-pages@v4, got {action}"
    
    def test_no_jekyll_build_action(self, all_steps):
        """Test that workflow doesn't use Jekyll build action (static content only)"""
        jekyll_steps = [s for s in all_steps if 'uses' in s and 'jekyll' in s['uses'].lower()]
        assert len(jekyll_steps) == 0, \
            "Static content workflow should not use Jekyll build actions"


class TestWorkflowComments:
    """Test comments and documentation in the workflow file"""
    
    def test_has_comments(self, workflow_raw):
        """Test that workflow file contains comments"""
        comment_lines = [line for line in workflow_raw.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) > 0, "Workflow should contain comments for documentation"
    
    def test_mentions_static_in_comments(self, workflow_raw):
        """Test that comments mention static content"""
        lower_content = workflow_raw.lower()
        assert 'static' in lower_content, \
            "Workflow should mention static content in comments or configuration"
    
    def test_mentions_github_pages_in_comments(self, workflow_raw):
        """Test that comments mention GitHub Pages"""
        lower_content = workflow_raw.lower()
        assert 'github pages' in lower_content or 'pages' in lower_content, \
            "Workflow should mention GitHub Pages"
    
    def test_mentions_entire_repository(self, workflow_raw):
        """Test that comments or configuration mention uploading entire repository"""
        lower_content = workflow_raw.lower()
        # Check for mentions of "entire" or "repository" in context of upload
        assert 'entire' in lower_content or 'repository' in lower_content, \
            "Workflow should indicate it uploads entire repository"


class TestEdgeCases:
    """Test edge cases and potential failure scenarios"""
    
    def test_no_syntax_errors_in_yaml(self, workflow_content):
        """Test that there are no YAML syntax errors"""
        assert workflow_content is not None, "YAML content should be loaded"
    
    def test_no_tabs_in_yaml(self, workflow_raw):
        """Test that workflow file doesn't use tabs (YAML should use spaces)"""
        assert '\t' not in workflow_raw, "YAML file should use spaces, not tabs"
    
    def test_consistent_indentation(self, workflow_raw):
        """Test that indentation is consistent throughout the file"""
        lines = workflow_raw.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    assert leading_spaces % 2 == 0, \
                        f"Line {i} has inconsistent indentation (not a multiple of 2)"
    
    def test_no_duplicate_job_names(self, workflow_content):
        """Test that there are no duplicate job names"""
        jobs = workflow_content.get('jobs', {})
        job_names = list(jobs.keys())
        assert len(job_names) == len(set(job_names)), "Duplicate job names found"
    
    def test_all_jobs_have_runner(self, workflow_content):
        """Test that all jobs specify a runner"""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            assert 'runs-on' in job_config, f"Job '{job_name}' missing 'runs-on' configuration"
    
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
    
    def test_no_duplicate_step_names_in_job(self, workflow_content):
        """Test that there are no duplicate step names within a job"""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            step_names = [s.get('name') for s in steps if 'name' in s]
            assert len(step_names) == len(set(step_names)), \
                f"Duplicate step names in job '{job_name}'"


class TestWorkflowSecurity:
    """Test security aspects of the workflow"""
    
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
    
    def test_permissions_follow_least_privilege(self, workflow_content):
        """Test that permissions follow least privilege principle"""
        permissions = workflow_content.get('permissions', {})
        
        # Check that write permissions are only granted where necessary
        write_perms = [k for k, v in permissions.items() if v == 'write']
        allowed_write = {'pages', 'id-token'}
        excessive_write = set(write_perms) - allowed_write
        
        assert len(excessive_write) == 0, \
            f"Excessive write permissions: {excessive_write}"
    
    def test_checkout_action_is_pinned_or_versioned(self, workflow_content):
        """Test that actions use version tags (security best practice)"""
        jobs = workflow_content.get('jobs', {})
        for _job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    action = step['uses']
                    assert '@' in action, f"Action '{action}' should specify a version"


class TestWorkflowFileProperties:
    """Test file properties and location"""
    
    def test_workflow_in_correct_directory(self, workflow_path):
        """Test that workflow is in .github/workflows directory"""
        assert '.github' in workflow_path.parts, "Workflow must be in .github directory"
        assert 'workflows' in workflow_path.parts, "Workflow must be in workflows subdirectory"
    
    def test_workflow_has_yml_extension(self, workflow_path):
        """Test that workflow file has .yml extension"""
        assert workflow_path.suffix in ['.yml', '.yaml'], \
            "Workflow must have .yml or .yaml extension"
    
    def test_workflow_file_is_readable(self, workflow_path):
        """Test that workflow file is readable"""
        assert os.access(workflow_path, os.R_OK), "Workflow file must be readable"


class TestSimplifiedWorkflow:
    """Test characteristics specific to simplified single-job deployment"""
    
    def test_no_separate_build_job(self, workflow_content):
        """Test that workflow doesn't have a separate build job"""
        jobs = workflow_content.get('jobs', {})
        assert 'build' not in jobs, \
            "Static workflow should not have separate build job (simplified deployment)"
    
    def test_single_job_contains_all_steps(self, workflow_content):
        """Test that the single deploy job contains all necessary steps"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job['steps']
        
        # Verify all key actions are present
        step_actions = [s.get('uses', '') for s in steps if 'uses' in s]
        
        has_checkout = any('checkout' in action for action in step_actions)
        has_configure = any('configure-pages' in action for action in step_actions)
        has_upload = any('upload-pages-artifact' in action for action in step_actions)
        has_deploy = any('deploy-pages' in action for action in step_actions)
        
        assert has_checkout, "Deploy job missing checkout step"
        assert has_configure, "Deploy job missing configure pages step"
        assert has_upload, "Deploy job missing upload artifact step"
        assert has_deploy, "Deploy job missing deploy pages step"


class TestStaticContentHandling:
    """Test static content-specific configuration"""
    
    def test_uploads_current_directory(self, workflow_content):
        """Test that workflow uploads current directory content"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job['steps']
        
        upload_steps = [s for s in steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "No upload step found"
        
        upload_step = upload_steps[0]
        path = upload_step.get('with', {}).get('path', '')
        assert path == '.', "Static workflow should upload current directory (.)"
    
    def test_no_build_output_directory(self, workflow_content):
        """Test that workflow doesn't reference build output directories"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job['steps']
        
        upload_steps = [s for s in steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        upload_step = upload_steps[0]
        path = upload_step.get('with', {}).get('path', '')
        
        # Should not reference typical build directories
        build_dirs = ['_site', 'dist', 'build', 'public', 'out']
        for build_dir in build_dirs:
            assert build_dir not in path, \
                f"Static workflow should not reference build directory '{build_dir}'"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])