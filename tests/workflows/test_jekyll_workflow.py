"""
Comprehensive test suite for .github/workflows/jekyll-gh-pages.yml

This test suite validates the GitHub Actions workflow configuration for Jekyll deployment including:
- YAML syntax and structure
- Workflow metadata (name, triggers)
- Branch configuration for main branch
- Permissions configuration for GitHub Pages
- Concurrency settings
- Job definitions and dependencies
- Build and deployment job configuration
- Step definitions and action versions
- Security and best practices
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
        # 'on' key is parsed as boolean True by PyYAML
        assert True in workflow_content or 'on' in workflow_content, "Workflow missing trigger configuration"
    
    def test_workflow_has_permissions(self, workflow_content):
        """Test that workflow has permissions configuration for GitHub Pages"""
        assert 'permissions' in workflow_content, "Workflow missing 'permissions' key"
    
    def test_workflow_has_concurrency(self, workflow_content):
        """Test that workflow has concurrency configuration"""
        assert 'concurrency' in workflow_content, "Workflow missing 'concurrency' key"


class TestWorkflowMetadata:
    """Test workflow metadata and configuration"""
    
    def test_workflow_name_is_defined(self, workflow_content):
        """Test that workflow has a name defined"""
        assert 'name' in workflow_content, "Workflow name not defined"
        assert isinstance(workflow_content['name'], str), "Workflow name must be a string"
        assert len(workflow_content['name']) > 0, "Workflow name cannot be empty"
    
    def test_workflow_name_mentions_jekyll(self, workflow_content):
        """Test that the workflow name mentions Jekyll"""
        name = workflow_content['name'].lower()
        assert 'jekyll' in name, f"Expected workflow name to mention 'jekyll', got '{workflow_content['name']}'"
    
    def test_workflow_name_mentions_github_pages(self, workflow_content):
        """Test that the workflow name mentions GitHub Pages"""
        name = workflow_content['name'].lower()
        assert 'github pages' in name or 'pages' in name, \
            f"Expected workflow name to mention 'pages', got '{workflow_content['name']}'"
    
    def test_workflow_has_triggers(self, workflow_content):
        """Test that workflow has trigger configuration"""
        triggers = workflow_content.get(True) or workflow_content.get('on')
        assert triggers is not None, "Workflow has no trigger configuration"


class TestBranchConfiguration:
    """Test branch configuration for main branch"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """Get trigger configuration from cached workflow content"""
        return workflow_content.get(True) or workflow_content.get('on')
    
    def test_push_trigger_exists(self, triggers):
        """Test that push trigger is configured"""
        assert 'push' in triggers, "Push trigger not configured"
    
    def test_workflow_dispatch_trigger_exists(self, triggers):
        """Test that workflow_dispatch trigger is configured"""
        assert 'workflow_dispatch' in triggers, "Workflow dispatch trigger not configured"
    
    def test_push_trigger_has_branches(self, triggers):
        """Test that push trigger has branch configuration"""
        push_config = triggers.get('push')
        assert push_config is not None, "Push trigger configuration is None"
        assert 'branches' in push_config, "Push trigger missing branches configuration"
    
    def test_push_branches_is_main(self, triggers):
        """Test that push trigger is configured for 'main' branch"""
        push_branches = triggers['push']['branches']
        assert isinstance(push_branches, list), "Push branches must be a list"
        assert 'main' in push_branches, "Push trigger must include 'main' branch"
    
    def test_only_main_branch_configured(self, triggers):
        """Test that only 'main' branch is configured"""
        push_branches = triggers['push']['branches']
        assert len(push_branches) == 1, f"Expected exactly 1 push branch, got {len(push_branches)}"
        assert push_branches[0] == 'main', f"Expected 'main' branch for push, got '{push_branches[0]}'"


class TestPermissionsConfiguration:
    """Test permissions configuration for GitHub Pages deployment"""
    
    @pytest.fixture
    def permissions(self, workflow_content):
        """Get permissions configuration from cached workflow content"""
        return workflow_content.get('permissions', {})
    
    def test_permissions_section_exists(self, workflow_content):
        """Test that permissions section exists"""
        assert 'permissions' in workflow_content, "Workflow missing 'permissions' section"
    
    def test_permissions_not_empty(self, permissions):
        """Test that permissions section is not empty"""
        assert len(permissions) > 0, "Permissions section is empty"
    
    def test_has_contents_permission(self, permissions):
        """Test that workflow has contents permission"""
        assert 'contents' in permissions, "Missing 'contents' permission"
    
    def test_contents_permission_is_read(self, permissions):
        """Test that contents permission is set to read"""
        assert permissions['contents'] == 'read', \
            f"Expected contents permission 'read', got '{permissions['contents']}'"
    
    def test_has_pages_permission(self, permissions):
        """Test that workflow has pages permission"""
        assert 'pages' in permissions, "Missing 'pages' permission"
    
    def test_pages_permission_is_write(self, permissions):
        """Test that pages permission is set to write"""
        assert permissions['pages'] == 'write', \
            f"Expected pages permission 'write', got '{permissions['pages']}'"
    
    def test_has_id_token_permission(self, permissions):
        """Test that workflow has id-token permission"""
        assert 'id-token' in permissions, "Missing 'id-token' permission"
    
    def test_id_token_permission_is_write(self, permissions):
        """Test that id-token permission is set to write"""
        assert permissions['id-token'] == 'write', \
            f"Expected id-token permission 'write', got '{permissions['id-token']}'"
    
    def test_permissions_follow_least_privilege(self, permissions):
        """Test that permissions follow principle of least privilege"""
        # Contents should be read-only, pages and id-token should be write
        assert permissions.get('contents') == 'read', "Contents should be read-only"
        assert permissions.get('pages') == 'write', "Pages needs write access"
        assert permissions.get('id-token') == 'write', "ID token needs write access"


class TestConcurrencyConfiguration:
    """Test concurrency configuration"""
    
    @pytest.fixture
    def concurrency(self, workflow_content):
        """Get concurrency configuration from cached workflow content"""
        return workflow_content.get('concurrency', {})
    
    def test_concurrency_section_exists(self, workflow_content):
        """Test that concurrency section exists"""
        assert 'concurrency' in workflow_content, "Workflow missing 'concurrency' section"
    
    def test_concurrency_has_group(self, concurrency):
        """Test that concurrency has group defined"""
        assert 'group' in concurrency, "Concurrency missing 'group' key"
    
    def test_concurrency_group_is_pages(self, concurrency):
        """Test that concurrency group is 'pages'"""
        assert concurrency['group'] == 'pages', \
            f"Expected concurrency group 'pages', got '{concurrency['group']}'"
    
    def test_concurrency_has_cancel_in_progress(self, concurrency):
        """Test that concurrency has cancel-in-progress setting"""
        assert 'cancel-in-progress' in concurrency, "Concurrency missing 'cancel-in-progress' key"
    
    def test_cancel_in_progress_is_false(self, concurrency):
        """Test that cancel-in-progress is set to false for production deployments"""
        assert concurrency['cancel-in-progress'] is False, \
            "cancel-in-progress should be false for production deployments"


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
    
    def test_deploy_job_exists(self, jobs):
        """Test that 'deploy' job is defined"""
        assert 'deploy' in jobs, "Deploy job not defined"
    
    def test_has_exactly_two_jobs(self, jobs):
        """Test that workflow has exactly two jobs (build and deploy)"""
        assert len(jobs) == 2, f"Expected exactly 2 jobs, got {len(jobs)}"


class TestBuildJobConfiguration:
    """Test build job configuration"""
    
    @pytest.fixture
    def build_job(self, workflow_content):
        """Get build job configuration from cached workflow content"""
        return workflow_content['jobs']['build']
    
    def test_build_job_has_runner(self, build_job):
        """Test that build job has a runner defined"""
        assert 'runs-on' in build_job, "Build job missing 'runs-on' configuration"
    
    def test_build_job_uses_ubuntu_latest(self, build_job):
        """Test that build job uses ubuntu-latest runner"""
        runner = build_job['runs-on']
        assert runner == 'ubuntu-latest', f"Expected 'ubuntu-latest' runner, got '{runner}'"
    
    def test_build_job_has_steps(self, build_job):
        """Test that build job has steps defined"""
        assert 'steps' in build_job, "Build job missing 'steps'"
        assert isinstance(build_job['steps'], list), "Steps must be a list"
        assert len(build_job['steps']) > 0, "Build job has no steps"
    
    def test_build_job_has_checkout_step(self, build_job):
        """Test that build job includes checkout action"""
        steps = build_job['steps']
        checkout_steps = [s for s in steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "Build job missing checkout step"
    
    def test_build_job_has_setup_pages_step(self, build_job):
        """Test that build job includes setup pages action"""
        steps = build_job['steps']
        setup_steps = [s for s in steps if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(setup_steps) > 0, "Build job missing setup pages step"
    
    def test_build_job_has_jekyll_build_step(self, build_job):
        """Test that build job includes Jekyll build action"""
        steps = build_job['steps']
        jekyll_steps = [s for s in steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "Build job missing Jekyll build step"
    
    def test_build_job_has_upload_artifact_step(self, build_job):
        """Test that build job includes upload artifact action"""
        steps = build_job['steps']
        upload_steps = [s for s in steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "Build job missing upload artifact step"
    
    def test_jekyll_build_step_has_config(self, build_job):
        """Test that Jekyll build step has source and destination configuration"""
        steps = build_job['steps']
        jekyll_steps = [s for s in steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "Jekyll build step not found"
        
        jekyll_step = jekyll_steps[0]
        assert 'with' in jekyll_step, "Jekyll build step missing 'with' configuration"
        assert 'source' in jekyll_step['with'], "Jekyll build missing 'source' configuration"
        assert 'destination' in jekyll_step['with'], "Jekyll build missing 'destination' configuration"
    
    def test_jekyll_build_source_is_root(self, build_job):
        """Test that Jekyll build source is the repository root"""
        steps = build_job['steps']
        jekyll_steps = [s for s in steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        jekyll_step = jekyll_steps[0]
        
        source = jekyll_step['with']['source']
        assert source == './', f"Expected Jekyll source './', got '{source}'"
    
    def test_jekyll_build_destination_is_site(self, build_job):
        """Test that Jekyll build destination is _site"""
        steps = build_job['steps']
        jekyll_steps = [s for s in steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        jekyll_step = jekyll_steps[0]
        
        destination = jekyll_step['with']['destination']
        assert destination == './_site', f"Expected Jekyll destination './_site', got '{destination}'"


class TestDeployJobConfiguration:
    """Test deploy job configuration"""
    
    @pytest.fixture
    def deploy_job(self, workflow_content):
        """Get deploy job configuration from cached workflow content"""
        return workflow_content['jobs']['deploy']
    
    def test_deploy_job_has_environment(self, deploy_job):
        """Test that deploy job has environment configuration"""
        assert 'environment' in deploy_job, "Deploy job missing 'environment' configuration"
    
    def test_deploy_environment_is_github_pages(self, deploy_job):
        """Test that deploy environment is github-pages"""
        env = deploy_job['environment']
        assert 'name' in env, "Environment missing 'name'"
        assert env['name'] == 'github-pages', \
            f"Expected environment 'github-pages', got '{env['name']}'"
    
    def test_deploy_environment_has_url(self, deploy_job):
        """Test that deploy environment has URL output"""
        env = deploy_job['environment']
        assert 'url' in env, "Environment missing 'url' configuration"
        assert '${{ steps.deployment.outputs.page_url }}' in env['url'], \
            "Environment URL should reference deployment output"
    
    def test_deploy_job_has_runner(self, deploy_job):
        """Test that deploy job has a runner defined"""
        assert 'runs-on' in deploy_job, "Deploy job missing 'runs-on' configuration"
    
    def test_deploy_job_uses_ubuntu_latest(self, deploy_job):
        """Test that deploy job uses ubuntu-latest runner"""
        runner = deploy_job['runs-on']
        assert runner == 'ubuntu-latest', f"Expected 'ubuntu-latest' runner, got '{runner}'"
    
    def test_deploy_job_depends_on_build(self, deploy_job):
        """Test that deploy job depends on build job"""
        assert 'needs' in deploy_job, "Deploy job missing 'needs' dependency"
        needs = deploy_job['needs']
        if isinstance(needs, str):
            assert needs == 'build', f"Deploy should depend on 'build', got '{needs}'"
        elif isinstance(needs, list):
            assert 'build' in needs, "Deploy should depend on 'build' job"
    
    def test_deploy_job_has_steps(self, deploy_job):
        """Test that deploy job has steps defined"""
        assert 'steps' in deploy_job, "Deploy job missing 'steps'"
        assert isinstance(deploy_job['steps'], list), "Steps must be a list"
        assert len(deploy_job['steps']) > 0, "Deploy job has no steps"
    
    def test_deploy_job_has_deploy_step(self, deploy_job):
        """Test that deploy job includes deploy pages action"""
        steps = deploy_job['steps']
        deploy_steps = [s for s in steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps) > 0, "Deploy job missing deploy pages step"
    
    def test_deploy_step_has_id(self, deploy_job):
        """Test that deploy step has an id for output reference"""
        steps = deploy_job['steps']
        deploy_steps = [s for s in steps if 'uses' in s and 'deploy-pages' in s['uses']]
        deploy_step = deploy_steps[0]
        
        assert 'id' in deploy_step, "Deploy step missing 'id'"
        assert deploy_step['id'] == 'deployment', \
            f"Expected deploy step id 'deployment', got '{deploy_step['id']}'"


class TestActionVersions:
    """Test that actions use appropriate versions"""
    
    @pytest.fixture
    def all_steps(self, workflow_content):
        """Get all steps from all jobs"""
        jobs = workflow_content.get('jobs', {})
        all_steps = []
        for job_config in jobs.values():
            all_steps.extend(job_config.get('steps', []))
        return all_steps
    
    def test_checkout_uses_v4(self, all_steps):
        """Test that checkout action uses version 4"""
        checkout_steps = [s for s in all_steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "No checkout step found"
        
        for step in checkout_steps:
            checkout_action = step['uses']
            assert 'actions/checkout@v4' in checkout_action, \
                f"Expected checkout@v4, got {checkout_action}"
    
    def test_configure_pages_uses_v5(self, all_steps):
        """Test that configure-pages action uses version 5"""
        config_steps = [s for s in all_steps if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(config_steps) > 0, "No configure-pages step found"
        
        for step in config_steps:
            action = step['uses']
            assert 'actions/configure-pages@v5' in action, \
                f"Expected configure-pages@v5, got {action}"
    
    def test_jekyll_build_uses_v1(self, all_steps):
        """Test that jekyll-build-pages action uses version 1"""
        jekyll_steps = [s for s in all_steps if 'uses' in s and 'jekyll-build-pages' in s['uses']]
        assert len(jekyll_steps) > 0, "No jekyll-build-pages step found"
        
        for step in jekyll_steps:
            action = step['uses']
            assert 'actions/jekyll-build-pages@v1' in action, \
                f"Expected jekyll-build-pages@v1, got {action}"
    
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
    
    def test_all_actions_are_versioned(self, all_steps):
        """Test that all actions use version tags (security best practice)"""
        for step in all_steps:
            if 'uses' in step:
                action = step['uses']
                assert '@' in action, f"Action '{action}' should specify a version"


class TestWorkflowComments:
    """Test comments and documentation in the workflow file"""
    
    def test_has_comments(self, workflow_raw):
        """Test that workflow file contains comments"""
        comment_lines = [line for line in workflow_raw.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) > 0, "Workflow should contain comments for documentation"
    
    def test_main_branch_comment_matches_config(self, workflow_raw):
        """Test that comments about main branch match the actual configuration"""
        assert 'main' in workflow_raw, "Workflow should mention 'main' branch"
    
    def test_mentions_github_pages(self, workflow_raw):
        """Test that workflow mentions GitHub Pages in comments"""
        lower_content = workflow_raw.lower()
        assert 'github pages' in lower_content or 'pages' in lower_content, \
            "Workflow should mention GitHub Pages"


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
    
    def test_no_duplicate_step_names_in_jobs(self, workflow_content):
        """Test that there are no duplicate step names within each job"""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            step_names = [s.get('name') for s in steps if 'name' in s]
            assert len(step_names) == len(set(step_names)), \
                f"Duplicate step names in job '{job_name}'"
    
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
                assert runner in valid_runners, \
                    f"Invalid runner '{runner}' in job '{job_name}'"
    
    def test_job_dependencies_are_valid(self, workflow_content):
        """Test that job dependencies reference existing jobs"""
        jobs = workflow_content.get('jobs', {})
        job_names = set(jobs.keys())
        
        for job_name, job_config in jobs.items():
            if 'needs' in job_config:
                needs = job_config['needs']
                if isinstance(needs, str):
                    needs = [needs]
                
                for dependency in needs:
                    assert dependency in job_names, \
                        f"Job '{job_name}' depends on non-existent job '{dependency}'"


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
    
    def test_permissions_are_restrictive(self, workflow_content):
        """Test that permissions follow principle of least privilege"""
        permissions = workflow_content.get('permissions', {})
        
        # Contents should not have write access
        if 'contents' in permissions:
            assert permissions['contents'] != 'write', \
                "Contents permission should not be 'write' for deployment"
    
    def test_uses_github_token_implicitly(self, workflow_raw):
        """Test that workflow uses GITHUB_TOKEN implicitly (no explicit token needed)"""
        # GitHub Actions provides GITHUB_TOKEN automatically
        # Explicit token usage might indicate security issues
        assert 'GITHUB_TOKEN' not in workflow_raw or 'secrets.GITHUB_TOKEN' in workflow_raw, \
            "Token usage should be through secrets context if explicitly referenced"


class TestWorkflowFilePermissions:
    """Test file permissions and location"""
    
    def test_workflow_in_correct_directory(self, workflow_path):
        """Test that workflow is in .github/workflows directory"""
        assert '.github' in workflow_path.parts, "Workflow must be in .github directory"
        assert 'workflows' in workflow_path.parts, "Workflow must be in workflows subdirectory"
    
    def test_workflow_has_yml_extension(self, workflow_path):
        """Test that workflow file has .yml extension"""
        assert workflow_path.suffix == '.yml', "Workflow must have .yml extension"
    
    def test_workflow_file_is_readable(self, workflow_path):
        """Test that workflow file is readable"""
        assert os.access(workflow_path, os.R_OK), "Workflow file must be readable"


class TestWorkflowBestPractices:
    """Test adherence to GitHub Actions best practices"""
    
    def test_concurrency_prevents_duplicate_deployments(self, workflow_content):
        """Test that concurrency configuration prevents duplicate deployments"""
        concurrency = workflow_content.get('concurrency', {})
        assert concurrency.get('group') is not None, \
            "Concurrency group should be defined to prevent duplicate runs"
    
    def test_deployment_uses_environment(self, workflow_content):
        """Test that deployment job uses environment for deployment tracking"""
        deploy_job = workflow_content['jobs'].get('deploy', {})
        assert 'environment' in deploy_job, \
            "Deploy job should use environment for tracking and protection"
    
    def test_build_and_deploy_are_separate(self, workflow_content):
        """Test that build and deploy are separate jobs (best practice)"""
        jobs = workflow_content.get('jobs', {})
        assert 'build' in jobs, "Should have separate build job"
        assert 'deploy' in jobs, "Should have separate deploy job"
        
        # Deploy should depend on build
        deploy_job = jobs['deploy']
        assert 'needs' in deploy_job, "Deploy job should depend on build job"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])