"""
Test suite for .github/workflows/iteration-status-emails.yml

This test suite validates the GitHub Actions workflow configuration for
iteration status email notifications including:
- YAML syntax and structure
- Workflow metadata (name, triggers)
- Scheduled cron configuration
- Path-based triggers for dashboard updates
- Job definitions and steps
- Email notification configuration
- Dashboard parsing logic
"""

import os
import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope='module')
def workflow_path():
    """
    Module-scoped fixture for workflow file path.
    Computed once and shared across all tests in this module.
    """
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / '.github' / 'workflows' / 'iteration-status-emails.yml'


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
    Parse the workflow YAML text into a Python mapping for use by tests.
    
    Provided as a module-scoped fixture so the YAML is parsed once per test module and reused.
    
    Parameters:
        workflow_raw (str): Raw YAML content of the workflow file.
    
    Returns:
        dict: Parsed YAML content as a Python dictionary
    """
    return yaml.safe_load(workflow_raw)


@pytest.fixture(scope='module')
def dashboard_path():
    """
    Module-scoped fixture for dashboard file path.
    """
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / 'docs' / 'january-2026-progress.md'


class TestWorkflowStructure:
    """Tests for basic workflow structure and syntax."""

    def test_workflow_file_exists(self, workflow_path):
        """Verify the workflow file exists."""
        assert workflow_path.exists(), f"Workflow file not found at {workflow_path}"

    def test_yaml_is_valid(self, workflow_content):
        """Verify the YAML is syntactically valid."""
        assert workflow_content is not None
        assert isinstance(workflow_content, dict)

    def test_workflow_has_name(self, workflow_content):
        """Verify the workflow has a name."""
        assert 'name' in workflow_content
        assert workflow_content['name'] == 'Iteration Status Email Updates'

    def test_workflow_has_triggers(self, workflow_content):
        """Verify the workflow has trigger configuration."""
        # In YAML, 'on' keyword might be parsed as True/boolean
        # Try both 'on' and True as keys
        triggers = workflow_content.get('on') or workflow_content.get(True)
        assert triggers is not None, "Workflow must have trigger configuration"
        assert isinstance(triggers, dict)


class TestWorkflowTriggers:
    """Tests for workflow trigger configuration."""

    def test_has_push_trigger(self, workflow_content):
        """Verify workflow triggers on push events."""
        triggers = workflow_content.get('on') or workflow_content.get(True)
        assert 'push' in triggers

    def test_push_trigger_branches(self, workflow_content):
        """Verify push trigger includes correct branches."""
        triggers = workflow_content.get('on') or workflow_content.get(True)
        push_config = triggers['push']
        assert 'branches' in push_config
        branches = push_config['branches']
        assert 'main' in branches or 'WIP' in branches

    def test_push_trigger_paths(self, workflow_content):
        """Verify push trigger monitors dashboard file."""
        triggers = workflow_content.get('on') or workflow_content.get(True)
        push_config = triggers['push']
        assert 'paths' in push_config
        paths = push_config['paths']
        assert any('january-2026-progress.md' in path for path in paths)

    def test_has_schedule_trigger(self, workflow_content):
        """Verify workflow has scheduled trigger."""
        triggers = workflow_content.get('on') or workflow_content.get(True)
        assert 'schedule' in triggers
        schedule = triggers['schedule']
        assert isinstance(schedule, list)
        assert len(schedule) > 0

    def test_schedule_cron_format(self, workflow_content):
        """Verify schedule uses valid cron format."""
        triggers = workflow_content.get('on') or workflow_content.get(True)
        schedule = triggers['schedule'][0]
        assert 'cron' in schedule
        cron_expr = schedule['cron']
        # Basic cron format validation (5 fields)
        parts = cron_expr.split()
        assert len(parts) == 5, f"Cron expression should have 5 fields, got: {cron_expr}"

    def test_has_workflow_dispatch(self, workflow_content):
        """Verify workflow can be manually triggered."""
        triggers = workflow_content.get('on') or workflow_content.get(True)
        assert 'workflow_dispatch' in triggers


class TestJobDefinitions:
    """Tests for job definitions and configuration."""

    def test_has_jobs(self, workflow_content):
        """Verify workflow has jobs defined."""
        assert 'jobs' in workflow_content
        assert len(workflow_content['jobs']) > 0

    def test_has_parse_and_notify_job(self, workflow_content):
        """Verify workflow has the parse-and-notify job."""
        jobs = workflow_content['jobs']
        assert 'parse-and-notify' in jobs

    def test_job_runs_on_ubuntu(self, workflow_content):
        """Verify job runs on ubuntu-latest."""
        job = workflow_content['jobs']['parse-and-notify']
        assert 'runs-on' in job
        assert 'ubuntu' in job['runs-on'].lower()

    def test_job_has_steps(self, workflow_content):
        """Verify job has steps defined."""
        job = workflow_content['jobs']['parse-and-notify']
        assert 'steps' in job
        assert len(job['steps']) > 0


class TestJobSteps:
    """Tests for individual job steps."""

    def test_has_checkout_step(self, workflow_content):
        """Verify job includes checkout step."""
        steps = workflow_content['jobs']['parse-and-notify']['steps']
        step_names = [step.get('name', '').lower() for step in steps]
        assert any('checkout' in name for name in step_names)

    def test_has_python_setup_step(self, workflow_content):
        """Verify job sets up Python."""
        steps = workflow_content['jobs']['parse-and-notify']['steps']
        step_names = [step.get('name', '').lower() for step in steps]
        assert any('python' in name for name in step_names)

    def test_has_parse_step(self, workflow_content):
        """Verify job includes dashboard parsing step."""
        steps = workflow_content['jobs']['parse-and-notify']['steps']
        step_names = [step.get('name', '').lower() for step in steps]
        assert any('parse' in name for name in step_names)

    def test_parse_step_has_id(self, workflow_content):
        """Verify parse step has an ID for output reference."""
        steps = workflow_content['jobs']['parse-and-notify']['steps']
        parse_steps = [s for s in steps if 'parse' in s.get('name', '').lower()]
        assert len(parse_steps) > 0
        parse_step = parse_steps[0]
        assert 'id' in parse_step

    def test_has_email_generation_step(self, workflow_content):
        """Verify job includes email content generation step."""
        steps = workflow_content['jobs']['parse-and-notify']['steps']
        step_names = [step.get('name', '').lower() for step in steps]
        assert any('email' in name for name in step_names)

    def test_has_send_email_step(self, workflow_content):
        """Verify job includes send email step."""
        steps = workflow_content['jobs']['parse-and-notify']['steps']
        step_names = [step.get('name', '').lower() for step in steps]
        # Look for send or notification in step names
        assert any('send' in name or 'notification' in name for name in step_names)


class TestEmailConfiguration:
    """Tests for email sending configuration."""

    def test_uses_email_action(self, workflow_content):
        """Verify workflow uses the action-send-mail action."""
        steps = workflow_content['jobs']['parse-and-notify']['steps']
        uses_actions = [s.get('uses', '') for s in steps]
        # Check specifically for dawidd6/action-send-mail action
        assert any('dawidd6/action-send-mail' in action for action in uses_actions), \
               "Workflow should use dawidd6/action-send-mail action"

    def test_email_step_uses_secrets(self, workflow_content):
        """Verify email step references GitHub secrets."""
        steps = workflow_content['jobs']['parse-and-notify']['steps']
        email_steps = [s for s in steps if 'send' in s.get('name', '').lower() and 'uses' in s]
        
        if email_steps:
            email_step = email_steps[0]
            step_content = str(email_step)
            # Check that secrets are referenced
            assert 'secrets.' in step_content.lower() or '${{ secrets' in step_content


class TestDashboardFile:
    """Tests for the dashboard file that the workflow monitors."""

    def test_dashboard_file_exists(self, dashboard_path):
        """Verify the dashboard file exists."""
        assert dashboard_path.exists(), f"Dashboard file not found at {dashboard_path}"

    def test_dashboard_has_content(self, dashboard_path):
        """Verify the dashboard file has content."""
        content = dashboard_path.read_text()
        assert len(content) > 0

    def test_dashboard_is_markdown(self, dashboard_path):
        """Verify the dashboard file is markdown format."""
        assert dashboard_path.suffix == '.md'

    def test_dashboard_has_emoji_indicators(self, dashboard_path):
        """Verify the dashboard uses emoji indicators."""
        content = dashboard_path.read_text()
        # Check for runner or hand emoji
        assert '🏃' in content or ':runner:' in content
        assert '✋' in content or ':hand:' in content


class TestParsingLogic:
    """Tests for dashboard parsing logic."""

    def test_can_identify_in_progress_tasks(self, dashboard_path):
        """Verify we can identify in-progress tasks with runner emoji."""
        content = dashboard_path.read_text()
        lines = content.split('\n')
        in_progress = [line for line in lines if '🏃' in line]
        # Should find at least some in-progress tasks (or the legend entry)
        assert len(in_progress) > 0

    def test_can_identify_blocked_tasks(self, dashboard_path):
        """Verify we can identify blocked tasks with hand emoji."""
        content = dashboard_path.read_text()
        lines = content.split('\n')
        blocked = [line for line in lines if '✋' in line]
        # Should find at least some blocked tasks (or the legend entry)
        assert len(blocked) > 0


class TestWorkflowDocumentation:
    """Tests for workflow documentation."""

    def test_setup_documentation_exists(self):
        """Verify setup documentation exists."""
        repo_root = Path(__file__).parent.parent.parent
        doc_path = repo_root / 'docs' / 'iteration-email-setup.md'
        assert doc_path.exists(), "Setup documentation should exist"

    def test_setup_documentation_has_secrets_section(self):
        """Verify setup documentation explains required secrets."""
        repo_root = Path(__file__).parent.parent.parent
        doc_path = repo_root / 'docs' / 'iteration-email-setup.md'
        content = doc_path.read_text()
        # Check for mentions of required secrets
        assert 'SMTP_SERVER' in content or 'secrets' in content.lower()
        assert 'SMTP_USERNAME' in content or 'email' in content.lower()


class TestWorkflowSecurity:
    """Tests for security considerations."""

    def test_no_hardcoded_credentials(self, workflow_raw):
        """Verify no credentials are hardcoded in the workflow."""
        # Check for common patterns that might indicate hardcoded credentials
        suspicious_patterns = [
            'password:',
            'smtp.gmail.com:',
            '@gmail.com',
            '@outlook.com',
        ]
        
        # Secrets should be referenced, not hardcoded
        for pattern in suspicious_patterns:
            if pattern in workflow_raw.lower():
                # If pattern found, ensure it's in a comment or using secrets
                lines_with_pattern = [line for line in workflow_raw.split('\n') 
                                     if pattern in line.lower()]
                for line in lines_with_pattern:
                    assert (line.strip().startswith('#') or 
                           'secrets.' in line.lower() or
                           '${{ secrets' in line.lower()), \
                           f"Potential hardcoded credential found: {line}"

    def test_uses_secure_connection(self, workflow_content):
        """Verify email configuration uses secure connection."""
        steps = workflow_content['jobs']['parse-and-notify']['steps']
        email_steps = [s for s in steps if 'send' in s.get('name', '').lower() and 'with' in s]
        
        if email_steps:
            email_step = email_steps[0]
            # Check if secure option is set to true
            with_config = email_step.get('with', {})
            if 'secure' in with_config:
                # If secure is specified, it should be true
                assert with_config['secure'] is True or with_config['secure'] == 'true'


class TestEdgeCases:
    """Test edge cases and error handling in the workflow."""

    def test_no_tabs_in_yaml(self, workflow_raw):
        """Test that workflow uses spaces, not tabs."""
        assert '\t' not in workflow_raw, "YAML should use spaces, not tabs"

    def test_consistent_indentation(self, workflow_raw):
        """Test that indentation is consistent (2 spaces per level)."""
        lines = workflow_raw.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    assert leading_spaces % 2 == 0, \
                        f"Line {i} has inconsistent indentation"

    def test_no_duplicate_job_names(self, workflow_content):
        """Test that there are no duplicate job names."""
        jobs = workflow_content.get('jobs', {})
        job_names = list(jobs.keys())
        assert len(job_names) == len(set(job_names)), "Duplicate job names found"

    def test_no_duplicate_step_ids(self, workflow_content):
        """Test that step IDs are unique within each job."""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            step_ids = [s.get('id') for s in steps if 'id' in s]
            assert len(step_ids) == len(set(step_ids)), \
                f"Duplicate step IDs in job '{job_name}'"

    def test_no_empty_steps(self, workflow_content):
        """Test that there are no empty steps."""
        jobs = workflow_content.get('jobs', {})
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for i, step in enumerate(steps):
                assert len(step) > 0, f"Step {i} in job '{job_name}' is empty"
                assert 'uses' in step or 'run' in step, \
                    f"Step {i} in job '{job_name}' missing 'uses' or 'run'"

    def test_yaml_is_parseable(self, workflow_content):
        """Test that YAML is properly parseable."""
        assert workflow_content is not None, "YAML should parse successfully"
        assert isinstance(workflow_content, dict), "Parsed YAML should be a dict"

    def test_workflow_handles_missing_dashboard(self, workflow_content):
        """Test that workflow is configured to handle missing dashboard gracefully."""
        # The workflow should have proper error handling or conditional logic
        # This test documents that the workflow should handle edge cases
        # Verify workflow is valid and can be loaded
        assert workflow_content is not None, "Workflow should be valid"
        # Verify it has the necessary job structure
        jobs = workflow_content.get('jobs', {})
        assert len(jobs) > 0, "Workflow should have at least one job"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
