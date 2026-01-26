"""
Comprehensive test suite for .github/workflows/static.yml

This test suite validates the GitHub Actions workflow for static content deployment including:
- YAML syntax and structure validation
- Workflow metadata and naming
- Trigger configuration (push and workflow_dispatch)
- Permissions configuration for GitHub Pages deployment
- Concurrency control settings
- Job definition (single deploy job)
- Step configurations and action versions
- Environment configuration
- Security best practices
- Edge cases and failure scenarios
"""

import pytest
import yaml
import os
import re
from pathlib import Path


# Pattern to detect suspicious key:value assignments in YAML workflows
# Matches: (password|api_key|secret/secrets): <non-empty-value>
HARDCODED_SECRET_PATTERN = re.compile(r'^\s*(password|api_key|secrets?)\s*:\s*(.+)$', re.IGNORECASE)


# Module-level fixtures to cache expensive operations
@pytest.fixture(scope='module')
def workflow_path():
    """
    Locate the repository's static GitHub Actions workflow file.
    
    Returns:
        Path: Path to the '.github/workflows/static.yml' file at the repository root.
    """
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / '.github' / 'workflows' / 'static.yml'


@pytest.fixture(scope='module')
def workflow_raw(workflow_path):
    """
    Pytest module-scoped fixture that provides the raw text contents of the workflow file.
    
    Parameters:
        workflow_path (str | pathlib.Path): Path to the workflow YAML file.
    
    Returns:
        str: Raw contents of the workflow file.
    """
    with open(workflow_path, 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def workflow_content(workflow_raw):
    """
    Parse YAML workflow text into a Python mapping.
    
    Parameters:
        workflow_raw (str): Raw YAML text of the workflow file.
    
    Returns:
        dict: Mapping representing the parsed workflow content.
    """
    return yaml.safe_load(workflow_raw)


@pytest.fixture(scope='module')
def jobs(workflow_content):
    """
    Return the top-level 'jobs' mapping from parsed workflow content.
    
    Parameters:
        workflow_content (dict): Parsed YAML mapping of the workflow.
    
    Returns:
        dict: The 'jobs' mapping if present, otherwise an empty dictionary.
    """
    return workflow_content.get('jobs', {})


@pytest.fixture(scope='module')
def permissions(workflow_content):
    """
    Retrieve the workflow's `permissions` mapping from the parsed workflow content.
    
    Parameters:
        workflow_content (dict): Parsed YAML mapping of the workflow file.
    
    Returns:
        dict: Mapping of permission names to access levels (e.g. `'contents': 'read'`). Returns an empty dict if the `permissions` key is absent.
    """
    return workflow_content.get('permissions', {})


@pytest.fixture(scope='module')
def concurrency(workflow_content):
    """
    Return the workflow's `concurrency` mapping.
    
    Parameters:
        workflow_content (dict): Parsed YAML mapping of the workflow file.
    
    Returns:
        dict: The `concurrency` mapping if present, otherwise an empty dict.
    """
    return workflow_content.get('concurrency', {})


class TestWorkflowStructure:
    """Test the basic structure and syntax of the static workflow file"""
    
    def test_workflow_file_exists(self, workflow_path):
        """Test that the static workflow file exists at the expected location"""
        assert workflow_path.exists(), f"Workflow file not found at {workflow_path}"
        assert workflow_path.is_file(), f"Expected file but found directory at {workflow_path}"
    
    def test_workflow_is_valid_yaml(self, workflow_content):
        """Test that the workflow file contains valid YAML"""
        assert workflow_content is not None, "Workflow content is None"
        assert isinstance(workflow_content, dict), "Workflow content must be a dictionary"
        assert len(workflow_content) > 0, "Workflow content is empty"
    
    def test_workflow_has_required_top_level_keys(self, workflow_content):
        """
        Verify the workflow defines required top-level keys and a trigger configuration.
        
        Parameters:
            workflow_content (dict): Parsed YAML mapping of the workflow file.
        
        This test asserts that the top-level keys 'name' and 'jobs' are present and that a trigger configuration exists (either an 'on' mapping or a top-level `True` value).
        """
        required_keys = ['name', 'jobs']
        for key in required_keys:
            assert key in workflow_content, f"Workflow missing required key '{key}'"
        
        # Check for trigger configuration
        assert True in workflow_content or 'on' in workflow_content, \
            "Workflow missing trigger configuration"
    
    def test_workflow_has_permissions_section(self, workflow_content):
        """
        Verify the workflow defines a top-level 'permissions' mapping.
        
        Asserts that the parsed workflow mapping contains a 'permissions' key required for GitHub Pages deployment.
        """
        assert 'permissions' in workflow_content, \
            "Workflow missing 'permissions' section required for Pages deployment"
    
    def test_workflow_has_concurrency_control(self, workflow_content):
        """
        Verify the workflow defines a top-level `concurrency` configuration for deployment control.
        """
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
    
    def test_workflow_name_mentions_static(self, workflow_content):
        """
        Ensure the workflow's name includes the word 'static' to indicate it deploys static content.
        """
        name = workflow_content['name'].lower()
        assert 'static' in name, "Workflow name should mention 'static' for clarity"
    
    def test_workflow_name_mentions_pages(self, workflow_content):
        """
        Ensure the workflow's top-level name includes the word "pages" (case-insensitive).
        """
        name = workflow_content['name'].lower()
        assert 'pages' in name, "Workflow name should mention 'Pages'"
    
    def test_workflow_name_is_descriptive(self, workflow_content):
        """
        Ensure the workflow's top-level 'name' is a descriptive phrase.
        
        Asserts that the workflow 'name' contains at least three words to promote clarity.
        """
        name = workflow_content['name']
        # Name should have at least 3 words for clarity
        word_count = len(name.split())
        assert word_count >= 3, \
            f"Workflow name should be descriptive (at least 3 words), got {word_count}"


class TestTriggerConfiguration:
    """Test trigger configuration for the workflow"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """
        Return the workflow's trigger configuration from parsed workflow content.
        
        Returns:
            dict or None: Trigger configuration mapping if present, `None` otherwise.
        """
        return workflow_content.get(True) or workflow_content.get('on')
    
    def test_has_trigger_configuration(self, triggers):
        """
        Verify the workflow defines a trigger configuration.
        
        Asserts that the `triggers` fixture represents a non-empty mapping corresponding to the workflow's `on` configuration.
        """
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
    
    def test_only_main_branch_in_push_trigger(self, triggers):
        """Test that push trigger only targets main branch"""
        branches = triggers['push']['branches']
        assert len(branches) == 1, \
            f"Push trigger should only have 'main' branch, got {len(branches)} branches"
        assert branches[0] == 'main', \
            f"Expected 'main' branch, got '{branches[0]}'"
    
    def test_has_workflow_dispatch(self, triggers):
        """
        Verify the workflow supports manual triggering via `workflow_dispatch`.
        """
        assert 'workflow_dispatch' in triggers, \
            "Workflow should support manual triggering via workflow_dispatch"
    
    def test_no_pull_request_trigger(self, triggers):
        """Test that workflow does not trigger on pull requests"""
        assert 'pull_request' not in triggers, \
            "Static deploy workflow should not trigger on pull requests"
    
    def test_only_two_triggers(self, triggers):
        """
        Verify the workflow defines exactly two triggers: `push` and `workflow_dispatch`.
        
        Parameters:
            triggers (dict): Mapping of the workflow's top-level trigger configuration (the parsed `on` section).
        """
        assert len(triggers) == 2, \
            f"Workflow should have exactly 2 triggers, got {len(triggers)}"


class TestPermissionsConfiguration:
    """Test permissions configuration for GitHub Pages deployment"""
    
    def test_permissions_section_exists(self, permissions):
        """
        Validate that the workflow defines a non-empty permissions mapping.
        
        Asserts that the `permissions` value exists, is a mapping, and contains at least one permission entry.
        
        Parameters:
            permissions (dict): The parsed 'permissions' mapping from the workflow YAML.
        """
        assert permissions is not None, "Permissions configuration is missing"
        assert isinstance(permissions, dict), "Permissions must be a dictionary"
        assert len(permissions) > 0, "Permissions section is empty"
    
    def test_has_contents_read_permission(self, permissions):
        """
        Verify the workflow declares a 'contents' permission with value 'read'.
        """
        assert 'contents' in permissions, "Missing 'contents' permission"
        assert permissions['contents'] == 'read', \
            "Contents permission should be 'read'"
    
    def test_has_pages_write_permission(self, permissions):
        """Test that workflow has pages write permission"""
        assert 'pages' in permissions, "Missing 'pages' permission"
        assert permissions['pages'] == 'write', \
            "Pages permission should be 'write' for deployment"
    
    def test_has_id_token_write_permission(self, permissions):
        """Test that workflow has id-token write permission for OIDC"""
        assert 'id-token' in permissions, "Missing 'id-token' permission"
        assert permissions['id-token'] == 'write', \
            "ID token permission should be 'write' for OIDC authentication"
    
    def test_exactly_three_permissions(self, permissions):
        """
        Ensure the workflow defines exactly three permission entries.
        
        Parameters:
            permissions (dict): Mapping of permission names to their configured values from the workflow.
        
        Raises:
            AssertionError: If the permissions mapping does not contain exactly three entries.
        """
        assert len(permissions) == 3, \
            f"Workflow should have exactly 3 permissions, got {len(permissions)}"
    
    def test_no_excessive_permissions(self, permissions):
        """
        Ensure the workflow only declares the minimal required permissions.
        
        Checks that the permissions mapping contains no keys other than 'contents', 'pages', and 'id-token'.
        
        Parameters:
            permissions (Mapping[str, Any]): Mapping of permission names to their configured values from the workflow.
        """
        allowed_permissions = {'contents', 'pages', 'id-token'}
        actual_permissions = set(permissions.keys())
        
        excessive = actual_permissions - allowed_permissions
        assert len(excessive) == 0, \
            f"Workflow has excessive permissions: {excessive}"
    
    def test_no_write_permission_on_contents(self, permissions):
        """Test that workflow doesn't have write access to contents"""
        contents_perm = permissions.get('contents')
        assert contents_perm != 'write', \
            "Workflow should not have write permission on contents (security)"


class TestConcurrencyConfiguration:
    """Test concurrency control configuration"""
    
    def test_concurrency_section_exists(self, concurrency):
        """Test that concurrency section is configured"""
        assert concurrency is not None, "Concurrency configuration is missing"
        assert isinstance(concurrency, dict), "Concurrency must be a dictionary"
    
    def test_has_concurrency_group(self, concurrency):
        """
        Ensure the concurrency configuration contains a non-empty 'group' string.
        
        Asserts that the 'group' key exists in the concurrency mapping and that its value is a non-empty string.
        """
        assert 'group' in concurrency, "Concurrency group not defined"
        group = concurrency['group']
        assert isinstance(group, str), "Concurrency group must be a string"
        assert len(group) > 0, "Concurrency group cannot be empty"
    
    def test_concurrency_group_is_pages(self, concurrency):
        """Test that concurrency group is set to 'pages'"""
        assert concurrency['group'] == 'pages', \
            "Concurrency group should be 'pages' for Pages deployments"
    
    def test_has_cancel_in_progress_setting(self, concurrency):
        """
        Verify the concurrency configuration defines the 'cancel-in-progress' setting.
        """
        assert 'cancel-in-progress' in concurrency, \
            "Concurrency missing 'cancel-in-progress' setting"
    
    def test_cancel_in_progress_is_false(self, concurrency):
        """Test that cancel-in-progress is false for production deployments"""
        assert concurrency['cancel-in-progress'] is False, \
            "cancel-in-progress should be False to allow production deployments to complete"
    
    def test_concurrency_config_matches_jekyll_workflow(self, concurrency):
        """
        Check that concurrency configuration uses the 'pages' group and does not cancel in-progress runs to match the Jekyll workflow.
        
        Parameters:
            concurrency (dict): The workflow's concurrency mapping.
        """
        # This ensures both deployment workflows use the same concurrency strategy
        assert concurrency['group'] == 'pages', \
            "Should use 'pages' group like Jekyll workflow"
        assert concurrency['cancel-in-progress'] is False, \
            "Should not cancel in-progress like Jekyll workflow"


class TestJobsConfiguration:
    """Test jobs configuration"""
    
    def test_jobs_section_exists(self, jobs):
        """
        Verify the workflow defines a non-empty top-level 'jobs' mapping.
        
        Parameters:
            jobs (dict): Parsed 'jobs' mapping from the workflow YAML; expected to be a mapping of job names to job definitions.
        """
        assert jobs is not None, "Jobs section is missing"
        assert len(jobs) > 0, "Jobs section is empty"
    
    def test_has_single_deploy_job(self, jobs):
        """Test that workflow has exactly one job (deploy)"""
        assert len(jobs) == 1, \
            f"Static workflow should have exactly 1 job, got {len(jobs)}"
    
    def test_job_is_named_deploy(self, jobs):
        """
        Assert that the workflow defines a job named 'deploy'.
        """
        assert 'deploy' in jobs, "Workflow should have 'deploy' job"
    
    def test_deploy_job_exists(self, jobs):
        """Test that deploy job is properly defined"""
        deploy_job = jobs.get('deploy')
        assert deploy_job is not None, "Deploy job not found"
        assert isinstance(deploy_job, dict), "Deploy job must be a dictionary"
    
    def test_deploy_job_has_runner(self, jobs):
        """Test that deploy job has runner configuration"""
        deploy_job = jobs.get('deploy', {})
        assert 'runs-on' in deploy_job, "Deploy job missing 'runs-on' configuration"
    
    def test_deploy_job_uses_ubuntu_latest(self, jobs):
        """Verify the deploy job is configured to run on the 'ubuntu-latest' runner."""
        runner = jobs['deploy']['runs-on']
        assert runner == 'ubuntu-latest', \
            f"Expected 'ubuntu-latest' runner, got '{runner}'"


class TestDeployJob:
    """Test deploy job configuration in detail"""
    
    @pytest.fixture
    def deploy_job(self, jobs):
        """
        Retrieve the configuration mapping for the 'deploy' job from the workflow jobs.
        
        Parameters:
            jobs (dict): Mapping of job names to their job configuration dictionaries.
        
        Returns:
            dict: The deploy job configuration if present, otherwise an empty dictionary.
        """
        return jobs.get('deploy', {})
    
    def test_deploy_job_has_environment(self, deploy_job):
        """Test that deploy job has environment configuration"""
        assert 'environment' in deploy_job, \
            "Deploy job missing 'environment' configuration"
    
    def test_environment_is_dict(self, deploy_job):
        """
        Verify the deploy job's 'environment' field is present and is a mapping.
        
        Asserts that the deploy job defines an 'environment' key whose value is a dictionary.
        """
        env = deploy_job.get('environment')
        assert isinstance(env, dict), "Environment must be a dictionary"
    
    def test_environment_name_is_github_pages(self, deploy_job):
        """Test that environment name is 'github-pages'"""
        env = deploy_job.get('environment', {})
        assert 'name' in env, "Environment missing 'name' field"
        assert env['name'] == 'github-pages', \
            "Environment name should be 'github-pages'"
    
    def test_environment_has_url_output(self, deploy_job):
        """
        Ensure the deploy job's environment exposes a GitHub Pages URL output.
        
        The environment's `url` must be a string, use GitHub expression delimiters `${{` and `}}`, and reference `deployment.outputs.page_url`.
        """
        env = deploy_job.get('environment', {})
        assert 'url' in env, "Environment missing 'url' field"
        url = env['url']
        assert isinstance(url, str), "Environment URL must be a string"
        assert '${{' in url and '}}' in url, \
            "Environment URL should use GitHub expressions"
        assert 'deployment.outputs.page_url' in url, \
            "URL should reference deployment step output"
    
    def test_deploy_job_has_no_dependencies(self, deploy_job):
        """Test that deploy job has no dependencies (single job workflow)"""
        assert 'needs' not in deploy_job, \
            "Deploy job should not have dependencies in single-job workflow"
    
    def test_deploy_job_has_steps(self, deploy_job):
        """Test that deploy job has steps defined"""
        assert 'steps' in deploy_job, "Deploy job missing 'steps'"
        steps = deploy_job['steps']
        assert isinstance(steps, list), "Steps must be a list"
        assert len(steps) > 0, "Deploy job has no steps"
    
    def test_deploy_job_has_four_steps(self, deploy_job):
        """Test that deploy job has exactly four steps"""
        steps = deploy_job.get('steps', [])
        assert len(steps) == 4, \
            f"Deploy job should have 4 steps, got {len(steps)}"


class TestDeploySteps:
    """Test individual steps in the deploy job"""
    
    @pytest.fixture
    def deploy_steps(self, jobs):
        """
        Get the steps list for the 'deploy' job from the workflow jobs mapping.
        
        Parameters:
            jobs (dict): Mapping of job names to job definitions as parsed from the workflow YAML.
        
        Returns:
            list: The list of step mappings for the 'deploy' job, or an empty list if the job or its steps are absent.
        """
        return jobs['deploy'].get('steps', [])
    
    def test_all_steps_have_names(self, deploy_steps):
        """
        Verify each step in the deploy job defines a non-empty string for the `name` field.
        
        Parameters:
            deploy_steps (list[dict]): Sequence of step mappings from the deploy job, each expected to include a `name` key whose value is a non-empty string.
        """
        for i, step in enumerate(deploy_steps):
            assert 'name' in step, f"Step {i} missing 'name' field"
            name = step['name']
            assert isinstance(name, str), f"Step {i} name must be a string"
            assert len(name) > 0, f"Step {i} name cannot be empty"
    
    def test_first_step_is_checkout(self, deploy_steps):
        """
        Verify the first deploy step uses a checkout action.
        
        Asserts that the first step in the deploy job defines a `uses` key and that its action string contains "checkout".
        """
        first_step = deploy_steps[0]
        assert 'uses' in first_step, "First step should use an action"
        assert 'checkout' in first_step['uses'].lower(), \
            "First step should be checkout action"
    
    def test_checkout_uses_v4(self, deploy_steps):
        """Test that checkout action uses version 4"""
        checkout_steps = [s for s in deploy_steps 
                         if 'uses' in s and 'checkout' in s['uses']]
        assert len(checkout_steps) > 0, "No checkout step found"
        assert '@v4' in checkout_steps[0]['uses'], \
            "Checkout action should use version 4"
    
    def test_has_setup_pages_step(self, deploy_steps):
        """Test that workflow includes setup pages action"""
        setup_steps = [s for s in deploy_steps 
                      if 'uses' in s and 'configure-pages' in s['uses']]
        assert len(setup_steps) > 0, "Missing Setup Pages step"
    
    def test_setup_pages_uses_v5(self, deploy_steps):
        """Test that setup pages action uses version 5"""
        setup_steps = [s for s in deploy_steps 
                      if 'uses' in s and 'configure-pages' in s['uses']]
        assert '@v5' in setup_steps[0]['uses'], \
            "Setup Pages should use version 5"
    
    def test_has_upload_artifact_step(self, deploy_steps):
        """Test that workflow includes upload artifact action"""
        upload_steps = [s for s in deploy_steps 
                       if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "Missing upload artifact step"
    
    def test_upload_artifact_uses_v3(self, deploy_steps):
        """
        Verify that the upload-pages-artifact action in the deploy steps specifies version v3.
        
        Parameters:
            deploy_steps (list[dict]): The list of step mappings from the deploy job in the workflow.
        """
        upload_steps = [s for s in deploy_steps 
                       if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert '@v3' in upload_steps[0]['uses'], \
            "Upload artifact should use version 3"
    
    def test_upload_artifact_has_path_parameter(self, deploy_steps):
        """
        Check that the upload-pages-artifact step defines a path parameter.
        
        Raises an assertion error if no step using the 'upload-pages-artifact' action is found, if that step has no 'with' mapping, or if the 'with' mapping lacks a 'path' key.
        
        Parameters:
            deploy_steps (list): Sequence of step mappings from the deploy job.
        """
        upload_steps = [s for s in deploy_steps 
                       if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "Upload artifact step not found"
        
        upload_step = upload_steps[0]
        assert 'with' in upload_step, "Upload artifact missing 'with' parameters"
        assert 'path' in upload_step['with'], "Upload artifact missing 'path' parameter"
    
    def test_upload_path_is_current_directory(self, deploy_steps):
        """Test that upload path is set to current directory (entire repo)"""
        upload_steps = [s for s in deploy_steps 
                       if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        path = upload_steps[0]['with']['path']
        assert path == '.', \
            "Upload path should be '.' to upload entire repository"
    
    def test_has_deploy_pages_step(self, deploy_steps):
        """Test that workflow includes deploy to pages action"""
        deploy_steps_filtered = [s for s in deploy_steps 
                                if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_steps_filtered) > 0, "Missing deploy to pages step"
    
    def test_deploy_pages_uses_v4(self, deploy_steps):
        """
        Verify the deploy-pages step references the v4 `deploy-pages` action.
        
        Asserts that a step whose `uses` value contains `deploy-pages` includes the `@v4` version tag.
        """
        deploy_step = [s for s in deploy_steps 
                      if 'uses' in s and 'deploy-pages' in s['uses']]
        assert '@v4' in deploy_step[0]['uses'], \
            "Deploy-pages should use version 4"
    
    def test_deploy_pages_has_id(self, deploy_steps):
        """Test that deploy pages step has ID for output reference"""
        deploy_step = [s for s in deploy_steps 
                      if 'uses' in s and 'deploy-pages' in s['uses']]
        assert len(deploy_step) > 0, "Deploy pages step not found"
        assert 'id' in deploy_step[0], "Deploy step missing 'id' for output reference"
        assert deploy_step[0]['id'] == 'deployment', \
            "Deploy step ID should be 'deployment'"
    
    def test_steps_are_in_correct_order(self, deploy_steps):
        """
        Verify the deploy job's action steps appear in the exact expected sequence.
        
        Asserts the `uses` action prefixes across the deploy steps equal:
        `actions/checkout`, `actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages`.
        
        Parameters:
            deploy_steps (list[dict]): Sequence of step mappings from the deploy job as parsed from the workflow.
        """
        step_actions = []
        for step in deploy_steps:
            if 'uses' in step:
                action = step['uses'].split('@')[0]
                step_actions.append(action)
        
        # Expected order: checkout, configure-pages, upload-artifact, deploy-pages
        expected_order = [
            'actions/checkout',
            'actions/configure-pages',
            'actions/upload-pages-artifact',
            'actions/deploy-pages'
        ]
        
        assert step_actions == expected_order, \
            f"Steps not in correct order. Expected {expected_order}, got {step_actions}"


class TestWorkflowComments:
    """Test comments and documentation in the workflow file"""
    
    def test_has_comments(self, workflow_raw):
        """Test that workflow file contains comments"""
        comment_lines = [line for line in workflow_raw.split('\n') 
                        if line.strip().startswith('#')]
        assert len(comment_lines) > 0, \
            "Workflow should contain comments for documentation"
    
    def test_has_simple_workflow_comment(self, workflow_raw):
        """
        Check the workflow file contains a comment that identifies it as a "simple" workflow.
        
        The test fails if the raw workflow content does not include the word "simple" (case-insensitive).
        """
        assert 'simple' in workflow_raw.lower() or 'Simple' in workflow_raw, \
            "Workflow should identify itself as a simple workflow"
    
    def test_mentions_static_in_comments(self, workflow_raw):
        """Test that comments mention static content"""
        assert 'static' in workflow_raw or 'Static' in workflow_raw, \
            "Comments should mention static content"
    
    def test_mentions_github_pages_in_comments(self, workflow_raw):
        """Test that comments mention GitHub Pages"""
        assert 'GitHub Pages' in workflow_raw or 'Pages' in workflow_raw, \
            "Comments should mention GitHub Pages"
    
    def test_has_descriptive_comment_for_deploy_job(self, workflow_raw):
        """
        Check that a descriptive comment appears near the deploy job definition.
        
        Ensures that within two lines before or after the line containing `deploy:` there is a comment or text mentioning `deploy` or `single`.
        """
        lines = workflow_raw.split('\n')
        for line in lines:
            if 'deploy:' in line:
                # Find comment before or after deploy job definition
                idx = lines.index(line)
                nearby_lines = lines[max(0, idx-2):min(len(lines), idx+2)]
                nearby_text = ' '.join(nearby_lines).lower()
                assert 'deploy' in nearby_text or 'single' in nearby_text, \
                    "Should have descriptive comment near deploy job"
                break


class TestEdgeCases:
    """Test edge cases and potential failure scenarios"""
    
    def test_no_yaml_syntax_errors(self, workflow_content):
        """Test that YAML is syntactically valid"""
        assert workflow_content is not None, "YAML content should be loaded"
    
    def test_no_tabs_in_yaml(self, workflow_raw):
        """
        Verify the workflow YAML uses spaces instead of tab characters.
        
        Asserts that the raw workflow content contains no tab characters, ensuring indentation is done with spaces.
        """
        assert '\t' not in workflow_raw, "YAML file should use spaces, not tabs"
    
    def test_consistent_indentation(self, workflow_raw):
        """
        Verify YAML indentation uses two-space increments for all non-empty, non-comment lines.
        
        Parameters:
            workflow_raw (str): Raw text content of the workflow file under test.
        """
        lines = workflow_raw.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    assert leading_spaces % 2 == 0, \
                        f"Line {i} has inconsistent indentation"
    
    def test_no_duplicate_step_names(self, jobs):
        """Test that there are no duplicate step names in deploy job"""
        deploy_job = jobs.get('deploy', {})
        steps = deploy_job.get('steps', [])
        step_names = [s.get('name') for s in steps if 'name' in s]
        assert len(step_names) == len(set(step_names)), \
            "Duplicate step names found in deploy job"
    
    def test_all_actions_are_versioned(self, jobs):
        """Test that all actions use version tags (security best practice)"""
        deploy_job = jobs.get('deploy', {})
        steps = deploy_job.get('steps', [])
        for step in steps:
            if 'uses' in step:
                action = step['uses']
                assert '@' in action, \
                    f"Action '{action}' should specify a version"
    
    def test_no_empty_steps(self, jobs):
        """
        Verify each step of the 'deploy' job is non-empty and contains either a `uses` action or a `run` command.
        
        Raises an assertion error identifying the step index if a step is empty or does not include either `uses` or `run`.
        """
        deploy_job = jobs.get('deploy', {})
        steps = deploy_job.get('steps', [])
        for i, step in enumerate(steps):
            assert len(step) > 0, f"Step {i} is empty"
            assert 'uses' in step or 'run' in step, \
                f"Step {i} must have either 'uses' or 'run'"


class TestWorkflowSecurity:
    """Test security aspects of the workflow"""
    
    def test_no_hardcoded_secrets(self, workflow_raw):
        """
        Check the workflow text for potential hardcoded secret literals and fail if any are not referenced via `secrets.` or a GitHub expression.
        
        Detects suspicious key:value assignments like `password: mypass` or `api_key: abc123` 
        but allows legitimate YAML keys like `secrets:` or `secrets: inherit` and GitHub expressions.
        
        Raises an assertion error when a line contains a suspicious key assigned a literal value.
        
        Parameters:
            workflow_raw (str): Raw contents of the workflow YAML file.
        """
        lines = workflow_raw.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comment lines
            if line.strip().startswith('#'):
                continue
            
            # Use module-level pattern to detect suspicious key:value assignments
            # Where value is not a GitHub expression (${{) or secrets. reference
            match = HARDCODED_SECRET_PATTERN.search(line)
            
            if match:
                key = match.group(1).lower()
                value = match.group(2).strip()
                
                # Allow "secrets:" with no value, "inherit", or other valid YAML null values
                if key == 'secrets' and (not value or value in ['inherit', '~', 'null']):
                    continue
                
                # Allow if value is a GitHub expression
                if value.startswith('${{'):
                    continue
                
                # Allow if value references secrets.
                if 'secrets.' in value:
                    continue
                
                # If we get here, it's a suspicious literal assignment
                assert False, \
                    f"Line {line_num}: Potential hardcoded secret '{key}: {value}' found"
    
    def test_uses_oidc_authentication(self, permissions):
        """Test that workflow uses OIDC for authentication"""
        assert 'id-token' in permissions, \
            "Workflow should use OIDC (id-token permission) for secure authentication"
        assert permissions['id-token'] == 'write', \
            "id-token permission should be 'write' for OIDC"
    
    def test_minimal_permissions_principle(self, permissions):
        """
        Ensure the workflow grants only the minimal set of permissions required for Pages deployment.
        
        Verifies there are exactly three permissions and that 'contents' is 'read', 'pages' is 'write', and 'id-token' is 'write'.
        """
        assert len(permissions) == 3, \
            "Workflow should have minimal permissions (exactly 3)"
        
        # Verify each permission is necessary
        assert permissions.get('contents') == 'read', \
            "Contents should be read-only"
        assert permissions.get('pages') == 'write', \
            "Pages write is necessary for deployment"
        assert permissions.get('id-token') == 'write', \
            "id-token write is necessary for OIDC"
    
    def test_no_script_injection_vulnerabilities(self, jobs):
        """Test that workflow doesn't have obvious script injection vulnerabilities"""
        deploy_job = jobs.get('deploy', {})
        steps = deploy_job.get('steps', [])
        
        for step in steps:
            if 'run' in step:
                run_command = step['run']
                # Check for potentially dangerous patterns
                dangerous_patterns = ['eval', 'exec', '$(', '`']
                for pattern in dangerous_patterns:
                    if pattern in run_command:
                        # Make sure it's not using untrusted input
                        assert '${{ github.event' not in run_command, \
                            f"Potential script injection vulnerability with {pattern}"


class TestWorkflowFilePermissions:
    """Test file permissions and location"""
    
    def test_workflow_in_correct_directory(self, workflow_path):
        """
        Verify the workflow file resides under the repository's .github/workflows directory.
        
        Asserts that the provided path contains both the '.github' and 'workflows' path components.
        """
        assert '.github' in workflow_path.parts, \
            "Workflow must be in .github directory"
        assert 'workflows' in workflow_path.parts, \
            "Workflow must be in workflows subdirectory"
    
    def test_workflow_has_yml_extension(self, workflow_path):
        """
        Verify the workflow filename uses the .yml extension.
        """
        assert workflow_path.suffix == '.yml', \
            "Workflow file should have .yml extension"
    
    def test_workflow_file_is_readable(self, workflow_path):
        """
        Verify the workflow file at the given path is readable by the current process.
        """
        assert os.access(workflow_path, os.R_OK), \
            "Workflow file must be readable"
    
    def test_workflow_filename_is_descriptive(self, workflow_path):
        """Test that workflow filename is descriptive"""
        filename = workflow_path.stem
        assert 'static' in filename, \
            "Workflow filename should mention 'static' for clarity"


class TestWorkflowDifferencesFromJekyll:
    """Test that static workflow appropriately differs from Jekyll workflow"""
    
    def test_no_jekyll_build_step(self, jobs):
        """Test that static workflow doesn't include Jekyll build (not needed)"""
        deploy_job = jobs.get('deploy', {})
        steps = deploy_job.get('steps', [])
        
        jekyll_steps = [s for s in steps 
                       if 'uses' in s and 'jekyll' in s['uses'].lower()]
        assert len(jekyll_steps) == 0, \
            "Static workflow should not include Jekyll build steps"
    
    def test_single_job_architecture(self, jobs):
        """
        Ensure the workflow defines exactly one job.
        """
        assert len(jobs) == 1, \
            "Static workflow should have single job (deploy only)"
    
    def test_uploads_entire_repository(self, jobs):
        """
        Verify the workflow uploads the entire repository to GitHub Pages.
        
        Checks that a step using the `upload-pages-artifact` action exists and that its `with.path` is '.'.
        """
        deploy_job = jobs.get('deploy', {})
        steps = deploy_job.get('steps', [])
        
        upload_steps = [s for s in steps 
                       if 'uses' in s and 'upload-pages-artifact' in s['uses']]
        assert len(upload_steps) > 0, "Upload step not found"
        
        path = upload_steps[0].get('with', {}).get('path', '')
        assert path == '.', \
            "Static workflow should upload entire repository (.)"


class TestStepNaming:
    """Test step naming conventions and clarity"""
    
    def test_all_step_names_are_capitalized(self, jobs):
        """Test that all step names use proper capitalization"""
        deploy_job = jobs.get('deploy', {})
        steps = deploy_job.get('steps', [])
        
        for step in steps:
            if 'name' in step:
                name = step['name']
                # First character should be uppercase
                assert name[0].isupper(), \
                    f"Step name should start with uppercase: '{name}'"
    
    def test_step_names_are_action_oriented(self, jobs):
        """
        Ensure each named step in the deploy job includes an action-oriented verb.
        
        Checks that every step with a `name` in the `deploy` job contains one of the expected action verbs: 'checkout', 'setup', 'upload', 'deploy', or 'configure'. The test fails if any named step does not include an action verb.
        """
        deploy_job = jobs.get('deploy', {})
        steps = deploy_job.get('steps', [])
        
        action_verbs = ['checkout', 'setup', 'upload', 'deploy', 'configure']
        for step in steps:
            if 'name' in step:
                name = step['name'].lower()
                has_action_verb = any(verb in name for verb in action_verbs)
                assert has_action_verb, \
                    f"Step name should contain action verb: '{step['name']}'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])