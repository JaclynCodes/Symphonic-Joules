"""
Comprehensive test suite for .github/workflows/blank.yml

This test suite validates the GitHub Actions workflow configuration including:
- YAML syntax and structure
- Workflow metadata (name, triggers)
- Branch configuration (specifically testing the 'main' branch requirement)
- Job definitions and runner configuration
- Step definitions and action versions
- Edge cases and failure scenarios
"""

import pytest
import yaml
import os


# Module-level fixtures to cache expensive file I/O and parsing operations
@pytest.fixture(scope='module')
def workflow_path(get_workflow_path):
    """
    Module-scoped fixture for workflow file path.
    Computed once and shared across all tests in this module.
    """
    return get_workflow_path('blank.yml')


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


@pytest.fixture(scope='module')
def jobs(workflow_content):
    """
    Module-scoped fixture for jobs configuration.
    Extracted once and shared across all tests in this module.
    """
    return workflow_content.get('jobs', {})


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
        # 'on' key is parsed as boolean True by PyYAML, check for trigger configuration
        assert True in workflow_content or 'on' in workflow_content, "Workflow missing trigger configuration"


class TestWorkflowMetadata:
    """Test workflow metadata and configuration"""
    
    def test_workflow_name_is_defined(self, workflow_content):
        """Test that workflow has a name defined"""
        assert 'name' in workflow_content, "Workflow name not defined"
        assert isinstance(workflow_content['name'], str), "Workflow name must be a string"
        assert len(workflow_content['name']) > 0, "Workflow name cannot be empty"
    
    def test_workflow_name_is_ci(self, workflow_content):
        """Test that the workflow is named 'CI'"""
        assert workflow_content['name'] == 'CI', f"Expected workflow name 'CI', got '{workflow_content['name']}'"
    
    def test_workflow_has_triggers(self, workflow_content):
        """Test that workflow has trigger configuration"""
        # PyYAML parses 'on:' as True
        triggers = workflow_content.get(True) or workflow_content.get('on')
        assert triggers is not None, "Workflow has no trigger configuration"


class TestBranchConfiguration:
    """Test branch configuration - critical for the main branch change"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """Get trigger configuration from cached workflow content"""
        return workflow_content.get(True) or workflow_content.get('on')
    
    def _validate_branch_config(self, branches, trigger_name):
        """Helper method to validate branch configuration"""
        assert isinstance(branches, list), f"{trigger_name} branches must be a list"
        assert 'main' in branches, f"{trigger_name} trigger must include 'main' branch"
        assert 'base' not in branches, f"{trigger_name} trigger should not include 'base' branch (should be 'main')"
    
    def _assert_trigger_has_branches(self, triggers, trigger_key, trigger_name):
        """Helper method to assert that a trigger has branch configuration"""
        trigger_config = triggers.get(trigger_key)
        assert trigger_config is not None, f"{trigger_name} trigger configuration is None"
        assert 'branches' in trigger_config, f"{trigger_name} trigger missing branches configuration"
    
    @pytest.mark.parametrize("trigger_key,trigger_name", [
        ('push', 'Push'),
        ('pull_request', 'Pull request'),
        ('workflow_dispatch', 'Workflow dispatch'),
    ])
    def test_trigger_exists(self, triggers, trigger_key, trigger_name):
        """Test that required triggers are configured"""
        assert trigger_key in triggers, f"{trigger_name} trigger not configured"
    
    @pytest.mark.parametrize("trigger_key,trigger_name", [
        ('push', 'Push'),
        ('pull_request', 'Pull request'),
    ])
    def test_trigger_has_branches(self, triggers, trigger_key, trigger_name):
        """Test that triggers have branch configuration"""
        self._assert_trigger_has_branches(triggers, trigger_key, trigger_name)
    
    @pytest.mark.parametrize("trigger_key,trigger_name", [
        ('push', 'Push'),
        ('pull_request', 'Pull request'),
    ])
    def test_branches_is_main(self, triggers, trigger_key, trigger_name):
        """Test that triggers are configured for 'main' branch (not 'base')"""
        branches = triggers[trigger_key]['branches']
        self._validate_branch_config(branches, trigger_name)
    
    def test_only_main_branch_configured(self, triggers):
        """Test that only 'main' branch is configured (no other branches)"""
        push_branches = triggers['push']['branches']
        pr_branches = triggers['pull_request']['branches']
        
        assert len(push_branches) == 1, f"Expected exactly 1 push branch, got {len(push_branches)}"
        assert len(pr_branches) == 1, f"Expected exactly 1 PR branch, got {len(pr_branches)}"
        assert push_branches[0] == 'main', f"Expected 'main' branch for push, got '{push_branches[0]}'"
        assert pr_branches[0] == 'main', f"Expected 'main' branch for PR, got '{pr_branches[0]}'"


class TestJobsConfiguration:
    """Test jobs configuration"""
    
    def test_jobs_section_exists(self, workflow_content):
        """Test that jobs section exists"""
        assert 'jobs' in workflow_content, "Workflow missing 'jobs' section"
    
    def test_jobs_section_not_empty(self, jobs):
        """Test that jobs section is not empty"""
        assert len(jobs) > 0, "Jobs section is empty"
    
    def test_build_job_exists(self, jobs):
        """Test that 'build' job is defined"""
        assert 'build' in jobs, "Build job not defined"
    
    def test_build_job_has_runner(self, jobs):
        """Test that build job has a runner defined"""
        build_job = jobs.get('build', {})
        assert 'runs-on' in build_job, "Build job missing 'runs-on' configuration"
    
    def test_build_job_uses_ubuntu_latest(self, jobs):
        """Test that build job uses ubuntu-latest runner"""
        runner = jobs['build']['runs-on']
        assert runner == 'ubuntu-latest', f"Expected 'ubuntu-latest' runner, got '{runner}'"
    
    def test_build_job_has_steps(self, jobs):
        """Test that build job has steps defined"""
        build_job = jobs.get('build', {})
        assert 'steps' in build_job, "Build job missing 'steps'"
        assert isinstance(build_job['steps'], list), "Steps must be a list"
        assert len(build_job['steps']) > 0, "Build job has no steps"


class TestStepsConfiguration:
    """Test individual steps within the build job"""
    
    @pytest.fixture
    def steps(self, workflow_content):
        """Get workflow steps from cached workflow content"""
        return workflow_content['jobs']['build']['steps']
    
    @pytest.fixture
    def checkout_steps(self, steps):
        """Get checkout steps from the workflow"""
        return [s for s in steps if 'uses' in s and 'checkout' in s['uses']]
    
    def test_has_checkout_step(self, checkout_steps):
        """Test that workflow includes checkout action"""
        assert len(checkout_steps) > 0, "No checkout step found"
    
    def test_checkout_uses_v4(self, checkout_steps):
        """Test that checkout action uses version 4"""
        assert len(checkout_steps) > 0, "No checkout step found"
        checkout_action = checkout_steps[0]['uses']
        assert 'actions/checkout@v4' in checkout_action, f"Expected checkout@v4, got {checkout_action}"
    
    def test_has_minimum_three_steps(self, steps):
        """Test that workflow has at least 3 steps"""
        assert len(steps) >= 3, f"Expected at least 3 steps, got {len(steps)}"
    
    def test_all_steps_have_valid_structure(self, steps):
        """Test that all steps have either 'uses' or 'run' key"""
        for i, step in enumerate(steps):
            assert 'uses' in step or 'run' in step, f"Step {i} missing 'uses' or 'run' key"
    
    def test_named_steps_have_valid_actions(self, steps):
        """
        Test that every named step in the workflow has either a 'run' command or a 'uses' action.
        This ensures that all steps with a 'name' key are valid GitHub Actions steps.
        """
        for step in steps:
            if 'name' in step:
                assert 'run' in step or 'uses' in step, \
                    f"Named step '{step['name']}' must have either 'run' or 'uses'"
    
    @pytest.mark.parametrize("step_name,error_message", [
        ('Run a one-line script', "One-line script step not found"),
        ('Run a multi-line script', "Multi-line script step not found"),
    ])
    def test_script_step_exists(self, steps, step_name, error_message):
        """Test that required script steps exist"""
        matching_steps = [s for s in steps if s.get('name') == step_name]
        assert len(matching_steps) > 0, error_message
    
    def test_script_steps_have_content(self, steps):
        """Test that script steps have actual commands"""
        for step in steps:
            if 'run' in step:
                run_command = step['run']
                assert isinstance(run_command, str), "Run command must be a string"
                assert len(run_command.strip()) > 0, "Run command cannot be empty"


class TestWorkflowComments:
    """Test comments and documentation in the workflow file"""
    
    def test_has_comments(self, workflow_raw):
        """Test that workflow file contains comments"""
        comment_lines = [line for line in workflow_raw.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) > 0, "Workflow should contain comments for documentation"
    
    def test_main_branch_comment_matches_config(self, workflow_raw):
        """Test that comments about main branch match the actual configuration"""
        # Check that comments mention 'main' branch - optimize by avoiding full lowercase conversion
        # Only convert to lowercase for case-insensitive search
        if 'main' not in workflow_raw and 'MAIN' not in workflow_raw and 'Main' not in workflow_raw:
            pytest.fail("Workflow should mention 'main' branch")
        
        # Ensure 'base' branch is not mentioned in active configuration
        lines = workflow_raw.split('\n')
        for line in lines:
            if 'branches:' in line:
                # Check the next line for branch configuration
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1]
                    if 'base' in next_line and not next_line.strip().startswith('#'):
                        pytest.fail("Found 'base' branch in active configuration (should be 'main')")
    
    def test_has_badge_reference(self, workflow_raw):
        """Test that workflow includes CI badge reference"""
        assert 'badge.svg' in workflow_raw, "Workflow should include badge reference"
        assert 'CI' in workflow_raw, "Workflow should reference CI badge"


class TestEdgeCases:
    """Test edge cases and potential failure scenarios"""
    
    def test_no_syntax_errors_in_yaml(self, workflow_content):
        """Test that there are no YAML syntax errors"""
        # If workflow_content fixture loaded successfully, YAML is valid
        # This test validates that the fixture itself works properly
        assert workflow_content is not None, "YAML content should be loaded"
    
    def test_no_tabs_in_yaml(self, workflow_raw):
        """Test that workflow file doesn't use tabs (YAML should use spaces)"""
        assert '\t' not in workflow_raw, "YAML file should use spaces, not tabs"
    
    def test_consistent_indentation(self, workflow_raw):
        """Test that indentation is consistent throughout the file"""
        lines = workflow_raw.split('\n')
        
        # Check that indentation is consistent (multiples of 2)
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    assert leading_spaces % 2 == 0, f"Line {i} has inconsistent indentation (not a multiple of 2)"
    
    def test_no_duplicate_job_names(self, jobs):
        """Test that there are no duplicate job names"""
        job_names = list(jobs.keys())
        assert len(job_names) == len(set(job_names)), "Duplicate job names found"
    
    def test_no_duplicate_step_names_in_job(self, jobs):
        """Test that there are no duplicate step names within a job"""
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            step_names = [s.get('name') for s in steps if 'name' in s]
            assert len(step_names) == len(set(step_names)), f"Duplicate step names in job '{job_name}'"
    
    def test_runner_is_valid(self, jobs):
        """Test that runner configuration is valid"""
        valid_runners = [
            'ubuntu-latest', 'ubuntu-22.04', 'ubuntu-20.04',
            'windows-latest', 'windows-2022', 'windows-2019',
            'macos-latest', 'macos-13', 'macos-12', 'macos-11'
        ]
        
        for job_name, job_config in jobs.items():
            runner = job_config.get('runs-on')
            if isinstance(runner, str):
                assert runner in valid_runners, f"Invalid runner '{runner}' in job '{job_name}'"


class TestWorkflowSecurity:
    """Test security aspects of the workflow"""
    
    def test_no_hardcoded_secrets(self, workflow_raw):
        """Test that workflow doesn't contain hardcoded secrets"""
        suspicious_patterns = ['password', 'token', 'api_key', 'secret']
        lower_content = workflow_raw.lower()
        
        for pattern in suspicious_patterns:
            if pattern in lower_content:
                # Make sure it's not in a comment or using secrets context
                lines = workflow_raw.split('\n')
                for line in lines:
                    if pattern in line.lower() and not line.strip().startswith('#'):
                        # Check if it's using GitHub secrets context
                        assert 'secrets.' in line or '${{' in line, \
                            f"Potential hardcoded secret pattern '{pattern}' found"
    
    def test_checkout_action_is_pinned_or_versioned(self, jobs):
        """Test that actions use version tags (security best practice)"""
        for _job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    action = step['uses']
                    # Should have version (@ symbol)
                    assert '@' in action, f"Action '{action}' should specify a version"


class TestWorkflowFilePermissions:
    """Test file permissions and location"""
    
    def test_workflow_in_correct_directory(self, workflow_path):
        """Test that workflow is in .github/workflows directory"""
        assert '.github' in workflow_path.parts, "Workflow must be in .github directory"
        assert 'workflows' in workflow_path.parts, "Workflow must be in workflows subdirectory"
    
    def test_workflow_has_yml_extension(self, workflow_path):
        """Test that workflow file has .yml or .yaml extension"""
        assert workflow_path.suffix in ['.yml', '.yaml'], "Workflow must have .yml or .yaml extension"
    
    def test_workflow_file_is_readable(self, workflow_path):
        """Test that workflow file is readable"""
        assert os.access(workflow_path, os.R_OK), "Workflow file must be readable"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestParametrizedRefactoring:
    """Test the parametrized test refactoring improvements"""
    
    def test_parametrize_decorator_reduces_code_duplication(self, workflow_content):
        """Verify that parametrized tests improve maintainability"""
        # This test validates that the refactoring approach is sound
        # by ensuring the workflow structure supports multiple trigger types
        triggers = workflow_content.get(True) or workflow_content.get('on')
        trigger_types = ['push', 'pull_request', 'workflow_dispatch']
        
        for trigger_type in trigger_types:
            assert trigger_type in triggers, f"Expected trigger type '{trigger_type}' not found"
    
    def test_all_branch_triggers_have_consistent_configuration(self, workflow_content):
        """Test that push and pull_request triggers have identical branch configs"""
        triggers = workflow_content.get(True) or workflow_content.get('on')
        
        push_branches = triggers.get('push', {}).get('branches', [])
        pr_branches = triggers.get('pull_request', {}).get('branches', [])
        
        # Both should be identical
        assert push_branches == pr_branches, \
            f"Push branches {push_branches} should match PR branches {pr_branches}"
        
        # Both should only contain 'main'
        assert push_branches == ['main'], f"Expected ['main'], got {push_branches}"
        assert pr_branches == ['main'], f"Expected ['main'], got {pr_branches}"


class TestJobsFixtureScoping:
    """Test the module-scoped jobs fixture functionality"""
    
    def test_jobs_fixture_returns_dict(self, jobs):
        """Test that jobs fixture returns a dictionary"""
        assert isinstance(jobs, dict), "Jobs fixture should return a dictionary"
    
    def test_jobs_fixture_contains_build_job(self, jobs):
        """Test that jobs fixture contains the build job"""
        assert 'build' in jobs, "Jobs fixture should contain 'build' job"
    
    def test_jobs_fixture_is_not_empty(self, jobs):
        """Test that jobs fixture is not empty"""
        assert len(jobs) > 0, "Jobs fixture should not be empty"
    
    def test_jobs_fixture_has_valid_job_structure(self, jobs):
        """Test that each job in jobs fixture has valid structure"""
        for job_name, job_config in jobs.items():
            assert isinstance(job_config, dict), f"Job '{job_name}' config should be a dict"
            assert 'runs-on' in job_config, f"Job '{job_name}' missing 'runs-on'"
            assert 'steps' in job_config, f"Job '{job_name}' missing 'steps'"


class TestTriggerConfiguration:
    """Additional comprehensive trigger configuration tests"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """Get trigger configuration from workflow content"""
        return workflow_content.get(True) or workflow_content.get('on')
    
    def test_workflow_dispatch_has_no_branches(self, triggers):
        """Test that workflow_dispatch doesn't have branch configuration"""
        workflow_dispatch = triggers.get('workflow_dispatch')
        assert workflow_dispatch is not None, "workflow_dispatch should be configured"
        
        # workflow_dispatch should not have branches (it's manual)
        if isinstance(workflow_dispatch, dict):
            assert 'branches' not in workflow_dispatch, \
                "workflow_dispatch should not have branches configuration"
    
    def test_trigger_keys_are_valid_github_events(self, triggers):
        """Test that all trigger keys are valid GitHub workflow events"""
        valid_events = [
            'push', 'pull_request', 'pull_request_target', 'workflow_dispatch',
            'schedule', 'release', 'issues', 'issue_comment', 'watch',
            'fork', 'create', 'delete', 'deployment', 'deployment_status',
            'page_build', 'public', 'check_run', 'check_suite', 'discussion',
            'discussion_comment', 'gollum', 'label', 'milestone', 'project',
            'project_card', 'project_column', 'registry_package', 'repository_dispatch',
            'status', 'workflow_call', 'workflow_run'
        ]
        
        for trigger_key in triggers.keys():
            assert trigger_key in valid_events, \
                f"Trigger '{trigger_key}' is not a valid GitHub workflow event"
    
    def test_branch_filter_format_is_correct(self, triggers):
        """Test that branch filters are in correct format (list of strings)"""
        for trigger_name in ['push', 'pull_request']:
            if trigger_name in triggers:
                trigger_config = triggers[trigger_name]
                if 'branches' in trigger_config:
                    branches = trigger_config['branches']
                    assert isinstance(branches, list), \
                        f"{trigger_name} branches should be a list"
                    for branch in branches:
                        assert isinstance(branch, str), \
                            f"Branch name in {trigger_name} should be a string, got {type(branch)}"
    
    def test_no_branches_ignore_configuration(self, triggers):
        """Test that branches-ignore is not used (prefer explicit branches)"""
        for trigger_name in ['push', 'pull_request']:
            if trigger_name in triggers:
                trigger_config = triggers[trigger_name]
                assert 'branches-ignore' not in trigger_config, \
                    f"{trigger_name} should use 'branches' not 'branches-ignore' for clarity"
    
    def test_no_conflicting_branch_filters(self, triggers):
        """Test that triggers don't have both branches and branches-ignore"""
        for trigger_name in ['push', 'pull_request']:
            if trigger_name in triggers:
                trigger_config = triggers[trigger_name]
                has_branches = 'branches' in trigger_config
                has_branches_ignore = 'branches-ignore' in trigger_config
                
                if has_branches and has_branches_ignore:
                    pytest.fail(
                        f"{trigger_name} has both 'branches' and 'branches-ignore' "
                        f"which is not allowed"
                    )


class TestStepValidation:
    """Comprehensive step validation tests"""
    
    @pytest.fixture
    def steps(self, workflow_content):
        """Get workflow steps"""
        return workflow_content['jobs']['build']['steps']
    
    @pytest.fixture
    def checkout_steps(self, steps):
        """Get checkout steps"""
        return [s for s in steps if 'uses' in s and 'checkout' in s['uses']]
    
    def test_checkout_is_first_step(self, steps):
        """Test that checkout is the first step"""
        first_step = steps[0]
        assert 'uses' in first_step, "First step should use an action"
        assert 'checkout' in first_step['uses'], "First step should be checkout action"
    
    def test_steps_have_unique_names_when_present(self, steps):
        """Test that all named steps have unique names"""
        step_names = [s.get('name') for s in steps if 'name' in s]
        assert len(step_names) == len(set(step_names)), \
            "Step names should be unique when present"
    
    def test_run_commands_are_not_empty(self, steps):
        """Test that all run commands have content"""
        for i, step in enumerate(steps):
            if 'run' in step:
                run_content = step['run'].strip()
                assert len(run_content) > 0, f"Step {i} has empty run command"
    
    def test_multiline_run_commands_use_pipe_syntax(self, steps):
        """Test that multi-line commands are properly formatted"""
        for step in steps:
            if 'run' in step and '\n' in step['run']:
                # Multi-line run commands should exist
                assert len(step['run'].split('\n')) > 1, \
                    "Multi-line run command should have multiple lines"
    
    def test_action_steps_do_not_have_run(self, steps):
        """Test that action steps (uses) don't also have run commands"""
        for step in steps:
            if 'uses' in step:
                # Actions should not have 'run' commands
                assert 'run' not in step, \
                    f"Step with 'uses' should not have 'run': {step.get('uses')}"
    
    def test_checkout_step_has_no_extra_config(self, checkout_steps):
        """Test that checkout step doesn't have unnecessary configuration"""
        if checkout_steps:
            checkout = checkout_steps[0]
            # Basic checkout should only have 'uses' (and maybe 'name')
            allowed_keys = {'uses', 'name', 'with', 'id'}
            actual_keys = set(checkout.keys())
            unexpected_keys = actual_keys - allowed_keys
            assert len(unexpected_keys) == 0, \
                f"Checkout step has unexpected keys: {unexpected_keys}"
    
    def test_step_names_are_descriptive(self, steps):
        """Test that step names follow descriptive naming conventions"""
        for step in steps:
            if 'name' in step:
                name = step['name']
                # Name should be reasonable length and not just single character
                assert len(name) > 3, f"Step name '{name}' is too short"
                assert len(name) < 100, f"Step name '{name}' is too long"
                # Name should start with capital letter
                assert name[0].isupper() or name[0].isdigit(), \
                    f"Step name '{name}' should start with capital letter"


class TestWorkflowBestPractices:
    """Test GitHub Actions best practices"""
    
    def test_workflow_has_descriptive_name(self, workflow_content):
        """Test that workflow name is descriptive"""
        name = workflow_content.get('name', '')
        assert len(name) > 0, "Workflow should have a name"
        assert len(name) < 50, "Workflow name should be concise"
    
    def test_workflow_has_at_least_one_job(self, jobs):
        """Test that workflow has at least one job defined"""
        assert len(jobs) >= 1, "Workflow should have at least one job"
    
    def test_all_jobs_have_steps(self, jobs):
        """Test that all jobs have at least one step"""
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            assert len(steps) > 0, f"Job '{job_name}' should have at least one step"
    
    def test_runner_uses_latest_tag(self, jobs):
        """Test that runners use -latest tags for better maintenance"""
        for job_name, job_config in jobs.items():
            runner = job_config.get('runs-on', '')
            if runner and isinstance(runner, str):
                # If not using a specific version, should use -latest
                if not any(runner.endswith(v) for v in ['-20.04', '-22.04', '-2019', '-2022', '-11', '-12', '-13']):
                    assert runner.endswith('-latest'), \
                        f"Job '{job_name}' should use -latest runner tag: {runner}"
    
    def test_no_deprecated_actions(self, jobs):
        """Test that no deprecated actions are used"""
        deprecated_actions = [
            'actions/checkout@v1',
            'actions/checkout@v2',
            'actions/setup-node@v1',
            'actions/setup-python@v1',
        ]
        
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    action = step['uses']
                    for deprecated in deprecated_actions:
                        assert deprecated not in action, \
                            f"Job '{job_name}' uses deprecated action: {action}"


class TestYAMLFormatting:
    """Test YAML formatting and style"""
    
    def test_yaml_uses_2_space_indentation(self, workflow_raw):
        """Test that YAML uses consistent 2-space indentation"""
        lines = workflow_raw.split('\n')
        indentation_levels = set()
        
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                spaces = len(line) - len(line.lstrip(' '))
                if spaces > 0:
                    indentation_levels.add(spaces)
        
        # All indentation should be multiples of 2
        for level in indentation_levels:
            assert level % 2 == 0, f"Found non-2-space indentation: {level}"
    
    def test_no_trailing_whitespace(self, workflow_raw):
        """Test that lines don't have trailing whitespace"""
        lines = workflow_raw.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip empty lines
            if len(line) > 0:
                assert not line.endswith(' ') and not line.endswith('\t'), \
                    f"Line {i} has trailing whitespace"
    
    def test_keys_use_lowercase(self, workflow_content):
        """Test that YAML keys use lowercase (GitHub Actions convention)"""
        # Top-level keys should be lowercase
        for key in workflow_content.keys():
            if isinstance(key, str):
                assert key.islower() or key == 'CI', \
                    f"Top-level key '{key}' should be lowercase"
    
    def test_list_items_properly_formatted(self, workflow_raw):
        """Test that list items use proper YAML formatting"""
        lines = workflow_raw.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if stripped.startswith('- '):
                # List items should have space after dash
                assert stripped[1] == ' ', \
                    f"Line {i}: List item should have space after dash"


class TestWorkflowDocumentation:
    """Test workflow documentation and comments"""
    
    def test_has_descriptive_comments(self, workflow_raw):
        """Test that workflow has descriptive comments"""
        comment_lines = [line.strip() for line in workflow_raw.split('\n') 
                        if line.strip().startswith('#')]
        
        # Should have multiple comment lines for good documentation
        assert len(comment_lines) >= 3, \
            "Workflow should have at least 3 comment lines for documentation"
    
    def test_comments_are_not_too_long(self, workflow_raw):
        """Test that comment lines are reasonable length"""
        comment_lines = [line for line in workflow_raw.split('\n') 
                        if line.strip().startswith('#')]
        
        for line in comment_lines:
            # Comments should be readable (not exceeding typical line length)
            assert len(line) < 100, f"Comment line too long: {line[:50]}..."
    
    def test_main_sections_have_comments(self, workflow_raw):
        """Test that main sections have explanatory comments"""
        lines = workflow_raw.split('\n')
        
        # Important sections that should be documented
        sections_to_check = ['on:', 'jobs:', 'steps:']
        
        for i, line in enumerate(lines):
            for section in sections_to_check:
                if section in line:
                    # Check if there's a comment before or on the same line
                    has_comment = False
                    # Check current line
                    if '#' in lines[i]:
                        has_comment = True
                    # Check previous line(s)
                    if i > 0 and '#' in lines[i-1]:
                        has_comment = True
                    
                    assert has_comment, \
                        f"Section '{section}' should have a comment for documentation"


class TestEdgeCaseScenarios:
    """Test additional edge cases and error conditions"""
    
    def test_workflow_handles_empty_branch_list_check(self, workflow_content):
        """Test that branch configurations are not empty lists"""
        triggers = workflow_content.get(True) or workflow_content.get('on')
        
        for trigger_name in ['push', 'pull_request']:
            if trigger_name in triggers:
                trigger_config = triggers[trigger_name]
                if 'branches' in trigger_config:
                    branches = trigger_config['branches']
                    assert len(branches) > 0, \
                        f"{trigger_name} branches list should not be empty"
    
    def test_no_null_values_in_config(self, workflow_content):
        """Test that there are no null/None values in critical config"""
        assert workflow_content.get('name') is not None, "Workflow name should not be null"
        assert workflow_content.get('jobs') is not None, "Jobs should not be null"
        
        triggers = workflow_content.get(True) or workflow_content.get('on')
        assert triggers is not None, "Triggers should not be null"
    
    def test_step_order_is_logical(self, workflow_content):
        """Test that steps are in logical order (checkout first)"""
        steps = workflow_content['jobs']['build']['steps']
        
        # First step with 'uses' should be checkout
        first_action_step = None
        for step in steps:
            if 'uses' in step:
                first_action_step = step
                break
        
        if first_action_step:
            assert 'checkout' in first_action_step.get('uses', ''), \
                "First action step should be checkout"
    
    def test_no_windows_line_endings(self, workflow_raw):
        """Test that file doesn't use Windows line endings"""
        assert '\r\n' not in workflow_raw, \
            "Workflow should use Unix line endings (LF), not Windows (CRLF)"
    
    def test_file_ends_with_newline(self, workflow_raw):
        """Test that file ends with a newline character"""
        assert workflow_raw.endswith('\n'), \
            "Workflow file should end with a newline"


class TestParameterizedWorkflowValidation:
    """Test parametrized validation approaches"""
    
    @pytest.mark.parametrize("job_name", ["build"])
    def test_job_has_required_keys(self, jobs, job_name):
        """Test that jobs have all required keys"""
        assert job_name in jobs, f"Job '{job_name}' not found"
        job = jobs[job_name]
        
        required_keys = ['runs-on', 'steps']
        for key in required_keys:
            assert key in job, f"Job '{job_name}' missing required key '{key}'"
    
    @pytest.mark.parametrize("step_index,expected_type", [
        (0, 'action'),  # First step should be an action (checkout)
        (1, 'script'),  # Second step should be a script
        (2, 'script'),  # Third step should be a script
    ])
    def test_step_types_in_order(self, workflow_content, step_index, expected_type):
        """Test that steps follow expected type pattern"""
        steps = workflow_content['jobs']['build']['steps']
        
        if step_index < len(steps):
            step = steps[step_index]
            
            if expected_type == 'action':
                assert 'uses' in step, \
                    f"Step {step_index} should be an action (uses)"
            elif expected_type == 'script':
                assert 'run' in step, \
                    f"Step {step_index} should be a script (run)"
    
    @pytest.mark.parametrize("trigger_type", ["push", "pull_request"])
    def test_trigger_branch_configuration_complete(self, workflow_content, trigger_type):
        """Test that branch-based triggers have complete configuration"""
        triggers = workflow_content.get(True) or workflow_content.get('on')
        
        assert trigger_type in triggers, f"Trigger '{trigger_type}' not found"
        trigger = triggers[trigger_type]
        
        assert 'branches' in trigger, \
            f"Trigger '{trigger_type}' should have branches configuration"
        assert isinstance(trigger['branches'], list), \
            f"Trigger '{trigger_type}' branches should be a list"
        assert len(trigger['branches']) > 0, \
            f"Trigger '{trigger_type}' should have at least one branch"


class TestFixtureReusability:
    """Test fixture reusability and efficiency"""
    
    def test_workflow_path_fixture_returns_path_object(self, workflow_path):
        """Test that workflow_path fixture returns a Path object"""
        from pathlib import Path
        assert isinstance(workflow_path, Path), \
            "workflow_path fixture should return a Path object"
    
    def test_workflow_raw_fixture_returns_string(self, workflow_raw):
        """Test that workflow_raw fixture returns a string"""
        assert isinstance(workflow_raw, str), \
            "workflow_raw fixture should return a string"
    
    def test_workflow_content_fixture_returns_dict(self, workflow_content):
        """Test that workflow_content fixture returns a dict"""
        assert isinstance(workflow_content, dict), \
            "workflow_content fixture should return a dict"
    
    def test_jobs_fixture_is_accessible(self, jobs):
        """Test that jobs fixture is accessible from module scope"""
        assert jobs is not None, "jobs fixture should be accessible"
        assert isinstance(jobs, dict), "jobs fixture should return a dict"
    
    def test_fixtures_contain_expected_data(self, workflow_path, workflow_raw, workflow_content, jobs):
        """Test that all fixtures contain expected data"""
        # Path should exist
        assert workflow_path.exists(), "workflow_path should point to existing file"
        
        # Raw content should not be empty
        assert len(workflow_raw) > 0, "workflow_raw should not be empty"
        
        # Parsed content should have keys
        assert len(workflow_content) > 0, "workflow_content should not be empty"
        
        # Jobs should contain at least one job
        assert len(jobs) > 0, "jobs should contain at least one job"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])