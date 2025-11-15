"""
Comprehensive test suite for .github/workflows/static.yml

This test suite validates the GitHub Actions workflow for static content deployment including:
- YAML syntax and structure
- Workflow metadata and permissions
- Trigger configuration (push to main, workflow_dispatch)
- Single deploy job configuration
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
    return repo_root / '.github' / 'workflows' / 'static.yml'


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
    
    def test_workflow_name_indicates_static_deployment(self, workflow_content):
        """Test that workflow name indicates static content deployment"""
        name = workflow_content['name']
        assert 'static' in name.lower() or 'deploy' in name.lower(), \
            f"Expected static/deploy in name, got '{name}'"
        assert 'Pages' in name or 'pages' in name.lower(), "Name should mention Pages"
    
    def test_workflow_name_format(self, workflow_content):
        """Test that workflow name is properly capitalized"""
        name = workflow_content['name']
        # First word should be capitalized
        words = name.split()
        assert len(words) > 0, "Name should have at least one word"
        assert words[0][0].isupper(), "First word should start with capital letter"


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
    
    def test_only_main_branch_in_push_trigger(self, triggers):
        """Test that push trigger only targets main branch"""
        push_config = triggers.get('push')
        branches = push_config['branches']
        assert len(branches) == 1, f"Expected only 'main' branch, got {branches}"
        assert branches[0] == 'main', f"Expected 'main', got '{branches[0]}'"
    
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
    
    def test_only_necessary_permissions(self, workflow_content):
        """Test that only necessary permissions are granted"""
        permissions = workflow_content.get('permissions', {})
        expected_permissions = {'contents', 'pages', 'id-token'}
        actual_permissions = set(permissions.keys())
        
        excessive = actual_permissions - expected_permissions
        assert len(excessive) == 0, f"Workflow has excessive permissions: {excessive}"
    
    def test_contents_not_writable(self, workflow_content):
        """Test that contents permission is read-only"""
        permissions = workflow_content.get('permissions', {})
        assert permissions.get('contents') != 'write', \
            "Static deployment should not need write access to contents"


class TestConcurrencyConfiguration:
    """Test concurrency settings for deployment workflows"""
    
    def test_has_concurrency_configuration(self, workflow_content):
        """Test that workflow defines concurrency settings"""
        assert 'concurrency' in workflow_content, "Deployment workflow should have concurrency settings"
    
    def test_concurrency_group_is_pages(self, workflow_content):
        """Test that concurrency group is set to 'pages'"""
        concurrency = workflow_content.get('concurrency', {})
        assert 'group' in concurrency, "Concurrency must define a group"
        assert concurrency['group'] == 'pages', "Concurrency group should be 'pages'"
    
    def test_cancel_in_progress_is_false(self, workflow_content):
        """Test that cancel-in-progress is set to false"""
        concurrency = workflow_content.get('concurrency', {})
        assert 'cancel-in-progress' in concurrency, "Should specify cancel-in-progress behavior"
        assert concurrency['cancel-in-progress'] is False, \
            "Should not cancel in-progress deployments (production safety)"
    
    def test_concurrency_configuration_is_complete(self, workflow_content):
        """Test that concurrency configuration has both required fields"""
        concurrency = workflow_content.get('concurrency', {})
        assert 'group' in concurrency and 'cancel-in-progress' in concurrency, \
            "Concurrency should have both 'group' and 'cancel-in-progress'"


class TestJobsConfiguration:
    """Test jobs configuration"""
    
    @pytest.fixture
    def jobs(self, workflow_content):
        """Get jobs configuration"""
        return workflow_content.get('jobs', {})
    
    def test_has_deploy_job(self, jobs):
        """Test that workflow has a deploy job"""
        assert 'deploy' in jobs, "Workflow should have 'deploy' job"
    
    def test_exactly_one_job(self, jobs):
        """Test that workflow has exactly one job (static deployment pattern)"""
        assert len(jobs) == 1, f"Expected 1 job for static deployment, found {len(jobs)}"
    
    def test_no_build_job(self, jobs):
        """Test that static workflow doesn't have separate build job"""
        assert 'build' not in jobs, "Static workflow should not have separate build job"


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
    
    def test_deploy_job_has_no_dependencies(self, deploy_job):
        """Test that deploy job has no dependencies (single job workflow)"""
        assert 'needs' not in deploy_job, "Single job workflow should not have dependencies"
    
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
    
    def test_has_all_required_steps(self, deploy_job):
        """Test that deploy job has all required steps"""
        steps = deploy_job['steps']
        step_actions = [s.get('uses', '') for s in steps]
        
        # Check for required actions
        assert any('checkout' in action for action in step_actions), "Must have checkout step"
        assert any('configure-pages' in action for action in step_actions), "Must configure pages"
        assert any('upload-pages-artifact' in action for action in step_actions), "Must upload artifact"
        assert any('deploy-pages' in action for action in step_actions), "Must deploy to pages"
    
    def test_steps_in_correct_order(self, deploy_job):
        """Test that steps are in logical order"""
        steps = deploy_job['steps']
        step_actions = [s.get('uses', '') for s in steps]
        
        checkout_idx = next(i for i, a in enumerate(step_actions) if 'checkout' in a)
        configure_idx = next(i for i, a in enumerate(step_actions) if 'configure-pages' in a)
        upload_idx = next(i for i, a in enumerate(step_actions) if 'upload-pages-artifact' in a)
        deploy_idx = next(i for i, a in enumerate(step_actions) if 'deploy-pages' in a)
        
        assert checkout_idx < configure_idx, "Checkout must come before configure"
        assert configure_idx < upload_idx, "Configure must come before upload"
        assert upload_idx < deploy_idx, "Upload must come before deploy"


class TestDeploySteps:
    """Test individual steps in the deploy job"""
    
    @pytest.fixture
    def steps(self, workflow_content):
        """Get deploy job steps"""
        return workflow_content['jobs']['deploy']['steps']
    
    def test_checkout_step_configuration(self, steps):
        """Test checkout step is properly configured"""
        checkout_steps = [s for s in steps if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) == 1, "Should have exactly one checkout step"
        
        checkout = checkout_steps[0]
        assert 'actions/checkout@v4' in checkout['uses'], "Should use checkout v4"
        assert 'name' in checkout, "Checkout step should have a name"
    
    def test_setup_pages_step_configuration(self, steps):
        """Test setup pages step is properly configured"""
        setup_steps = [s for s in steps if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(setup_steps) == 1, "Should have exactly one setup pages step"
        
        setup = setup_steps[0]
        assert 'actions/configure-pages@v5' in setup['uses'], "Should use configure-pages v5"
        assert 'name' in setup, "Setup step should have a name"
    
    def test_upload_artifact_step_configuration(self, steps):
        """Test upload artifact step is properly configured"""
        upload_steps = [s for s in steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) == 1, "Should have exactly one upload step"
        
        upload = upload_steps[0]
        assert 'actions/upload-pages-artifact@v3' in upload['uses'], "Should use upload-pages-artifact v3"
        assert 'name' in upload, "Upload step should have a name"
    
    def test_upload_artifact_has_path_configuration(self, steps):
        """Test that upload artifact specifies what to upload"""
        upload_steps = [s for s in steps if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "Upload step not found"
        
        upload = upload_steps[0]
        assert 'with' in upload, "Upload step should have 'with' configuration"
        assert 'path' in upload['with'], "Upload should specify path"
        
        # Path should upload entire repository for static content
        path = upload['with']['path']
        assert path == '.' or path == './', "Should upload entire repository"
    
    def test_deploy_pages_step_configuration(self, steps):
        """Test deploy pages step is properly configured"""
        deploy_steps = [s for s in steps if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps) == 1, "Should have exactly one deploy step"
        
        deploy = deploy_steps[0]
        assert 'actions/deploy-pages@v4' in deploy['uses'], "Should use deploy-pages v4"
        assert 'name' in deploy, "Deploy step should have a name"
        assert 'id' in deploy, "Deploy step should have an ID"
        assert deploy['id'] == 'deployment', "Deploy step ID should be 'deployment'"


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
                    assert '@' in action, f"Action '{action}' should specify version"
    
    def test_actions_use_current_versions(self, workflow_content):
        """Test that actions use recommended versions"""
        jobs = workflow_content.get('jobs', {})
        for job_config in jobs.values():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' not in step:
                    continue
                    
                action = step['uses']
                if 'checkout' in action:
                    assert '@v4' in action or '@v5' in action, "Checkout should use v4 or newer"
                elif 'configure-pages' in action:
                    assert '@v5' in action or '@v6' in action, "Configure-pages should use v5 or newer"
                elif 'upload-pages-artifact' in action:
                    assert '@v3' in action or '@v4' in action, "Upload-pages-artifact should use v3 or newer"
                elif 'deploy-pages' in action:
                    assert '@v4' in action or '@v5' in action, "Deploy-pages should use v4 or newer"


class TestStepNames:
    """Test that steps have descriptive names"""
    
    def test_all_steps_have_names(self, workflow_content):
        """Test that all steps have descriptive names"""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for i, step in enumerate(steps):
                assert 'name' in step, f"Step {i} in job '{job_name}' should have a name"
                assert len(step['name']) > 0, f"Step {i} name should not be empty"
    
    def test_step_names_are_descriptive(self, workflow_content):
        """Test that step names are clear and descriptive"""
        jobs = workflow_content.get('jobs', {})
        for job_config in jobs.values():
            steps = job_config.get('steps', [])
            for step in steps:
                name = step.get('name', '')
                # Names should be more than just action names
                assert len(name.split()) >= 2 or name in ['Checkout', 'Deploy'], \
                    f"Step name '{name}' should be more descriptive"


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
    
    def test_file_ends_with_newline(self, workflow_raw):
        """Test that file ends with a newline"""
        assert workflow_raw.endswith('\n'), "File should end with newline"


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
    
    def test_no_matrix_strategy(self, workflow_content):
        """Test that static deployment doesn't use matrix (unnecessary complexity)"""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            assert 'strategy' not in job_config, \
                f"Static deployment job '{job_name}' should not use matrix strategy"


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
    
    def test_permissions_follow_least_privilege(self, workflow_content):
        """Test that permissions follow principle of least privilege"""
        permissions = workflow_content.get('permissions', {})
        
        # Contents should be read-only
        assert permissions.get('contents') == 'read', \
            "Contents should be read-only for static deployment"
        
        # Should not have unnecessary permissions
        dangerous_permissions = ['packages', 'actions', 'checks', 'deployments', 
                                'discussions', 'issues', 'pull-requests', 'statuses']
        for perm in dangerous_permissions:
            assert perm not in permissions, \
                f"Static deployment should not need '{perm}' permission"


class TestCommentDocumentation:
    """Test that workflow has appropriate documentation"""
    
    def test_has_descriptive_header_comment(self, workflow_raw):
        """Test that workflow has a descriptive header comment"""
        lines = workflow_raw.split('\n')
        # First non-empty line should be a comment
        first_line = next((line for line in lines if line.strip()), '')
        assert first_line.strip().startswith('#'), "File should start with a comment"
    
    def test_comments_explain_purpose(self, workflow_raw):
        """Test that comments explain the workflow's purpose"""
        comment_text = ' '.join(line.strip('# ').lower() 
                               for line in workflow_raw.split('\n') 
                               if line.strip().startswith('#'))
        
        # Comments should mention deployment or pages
        assert 'deploy' in comment_text or 'pages' in comment_text, \
            "Comments should explain deployment purpose"


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
    
    def test_workflow_filename_is_appropriate(self, workflow_path):
        """Test that workflow filename reflects its purpose"""
        filename = workflow_path.stem
        assert 'static' in filename.lower() or 'pages' in filename.lower() or 'deploy' in filename.lower(), \
            "Filename should reflect static deployment purpose"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])