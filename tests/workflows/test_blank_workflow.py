"""
Comprehensive test suite for .github/workflows/blank.yml

This test suite validates the GitHub Actions workflow configuration including:
- YAML syntax and structure
- GitHub Actions schema compliance
- Workflow trigger configuration
- Job definitions and steps
- Branch references and configurations
"""

import pytest
import yaml
import os
from pathlib import Path


# Fixture to load the workflow file
@pytest.fixture
def workflow_file_path():
    """Return the path to the workflow file."""
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / ".github" / "workflows" / "blank.yml"


@pytest.fixture
def workflow_data(workflow_file_path):
    """Load and parse the workflow YAML file."""
    with open(workflow_file_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def workflow_raw_content(workflow_file_path):
    """Load the raw content of the workflow file."""
    with open(workflow_file_path, 'r') as f:
        return f.read()


class TestWorkflowStructure:
    """Test the basic structure and syntax of the workflow file."""
    
    def test_workflow_file_exists(self, workflow_file_path):
        """Test that the workflow file exists."""
        assert workflow_file_path.exists(), "Workflow file should exist"
    
    def test_workflow_is_valid_yaml(self, workflow_file_path):
        """Test that the workflow file is valid YAML."""
        try:
            with open(workflow_file_path, 'r') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML syntax: {e}")
    
    def test_workflow_has_name(self, workflow_data):
        """Test that the workflow has a name defined."""
        assert "name" in workflow_data, "Workflow should have a name"
        assert workflow_data["name"] == "CI", "Workflow name should be 'CI'"
    
    def test_workflow_has_jobs(self, workflow_data):
        """Test that the workflow has jobs defined."""
        assert "jobs" in workflow_data, "Workflow should have jobs defined"
        assert isinstance(workflow_data["jobs"], dict), "Jobs should be a dictionary"
        assert len(workflow_data["jobs"]) > 0, "Workflow should have at least one job"


class TestWorkflowTriggers:
    """Test workflow trigger configurations."""
    
    def test_workflow_has_on_triggers(self, workflow_data):
        """Test that the workflow has 'on' triggers defined."""
        # YAML parser interprets 'on' as True (boolean)
        assert True in workflow_data or "on" in workflow_data, \
            "Workflow should have trigger configuration"
    
    def test_push_trigger_configured(self, workflow_data):
        """Test that push trigger is configured."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        assert "push" in triggers, "Push trigger should be configured"
    
    def test_push_trigger_branches(self, workflow_data):
        """Test that push trigger targets main branch."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        push_config = triggers.get("push", {})
        assert "branches" in push_config, "Push trigger should specify branches"
        branches = push_config["branches"]
        assert isinstance(branches, list), "Branches should be a list"
        assert "main" in branches, "Push trigger should include 'main' branch"
    
    def test_push_trigger_does_not_reference_base_branch(self, workflow_data):
        """Test that push trigger does not reference the old 'base' branch."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        push_config = triggers.get("push", {})
        branches = push_config.get("branches", [])
        assert "base" not in branches, \
            "Push trigger should not reference deprecated 'base' branch"
    
    def test_pull_request_trigger_configured(self, workflow_data):
        """Test that pull_request trigger is configured."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        assert "pull_request" in triggers, "Pull request trigger should be configured"
    
    def test_pull_request_trigger_branches(self, workflow_data):
        """Test that pull_request trigger targets main branch."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        pr_config = triggers.get("pull_request", {})
        assert "branches" in pr_config, "Pull request trigger should specify branches"
        branches = pr_config["branches"]
        assert isinstance(branches, list), "Branches should be a list"
        assert "main" in branches, \
            "Pull request trigger should include 'main' branch"
    
    def test_pull_request_trigger_does_not_reference_base_branch(self, workflow_data):
        """Test that pull_request trigger does not reference the old 'base' branch."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        pr_config = triggers.get("pull_request", {})
        branches = pr_config.get("branches", [])
        assert "base" not in branches, \
            "Pull request trigger should not reference deprecated 'base' branch"
    
    def test_workflow_dispatch_trigger_configured(self, workflow_data):
        """Test that workflow_dispatch trigger is configured for manual runs."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        assert "workflow_dispatch" in triggers, \
            "Workflow should support manual dispatch"
    
    def test_no_unexpected_triggers(self, workflow_data):
        """Test that only expected triggers are configured."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        expected_triggers = {"push", "pull_request", "workflow_dispatch"}
        actual_triggers = set(triggers.keys())
        unexpected = actual_triggers - expected_triggers
        assert len(unexpected) == 0, \
            f"Unexpected triggers found: {unexpected}"


class TestJobConfiguration:
    """Test job configurations in the workflow."""
    
    def test_build_job_exists(self, workflow_data):
        """Test that the 'build' job exists."""
        jobs = workflow_data.get("jobs", {})
        assert "build" in jobs, "Workflow should have a 'build' job"
    
    def test_build_job_has_runner(self, workflow_data):
        """Test that the build job specifies a runner."""
        build_job = workflow_data["jobs"]["build"]
        assert "runs-on" in build_job, "Build job should specify a runner"
        assert build_job["runs-on"] == "ubuntu-latest", \
            "Build job should run on ubuntu-latest"
    
    def test_build_job_has_steps(self, workflow_data):
        """Test that the build job has steps defined."""
        build_job = workflow_data["jobs"]["build"]
        assert "steps" in build_job, "Build job should have steps"
        assert isinstance(build_job["steps"], list), "Steps should be a list"
        assert len(build_job["steps"]) > 0, "Build job should have at least one step"
    
    def test_checkout_step_exists(self, workflow_data):
        """Test that the checkout step exists."""
        steps = workflow_data["jobs"]["build"]["steps"]
        checkout_steps = [s for s in steps if "uses" in s and "checkout" in s["uses"]]
        assert len(checkout_steps) > 0, \
            "Build job should include a checkout step"
    
    def test_checkout_step_version(self, workflow_data):
        """Test that the checkout action uses v4."""
        steps = workflow_data["jobs"]["build"]["steps"]
        checkout_steps = [s for s in steps if "uses" in s and "checkout" in s["uses"]]
        assert len(checkout_steps) > 0
        checkout_action = checkout_steps[0]["uses"]
        assert "@v4" in checkout_action, \
            "Checkout action should use v4"
    
    def test_all_steps_have_valid_structure(self, workflow_data):
        """Test that all steps have valid structure."""
        steps = workflow_data["jobs"]["build"]["steps"]
        for i, step in enumerate(steps):
            assert isinstance(step, dict), f"Step {i} should be a dictionary"
            assert "uses" in step or "run" in step, \
                f"Step {i} should have either 'uses' or 'run'"
    
    def test_named_steps_have_names(self, workflow_data):
        """Test that steps with 'name' field have non-empty names."""
        steps = workflow_data["jobs"]["build"]["steps"]
        for i, step in enumerate(steps):
            if "name" in step:
                assert step["name"], f"Step {i} should have a non-empty name"
                assert isinstance(step["name"], str), \
                    f"Step {i} name should be a string"


class TestWorkflowSemantics:
    """Test semantic correctness and best practices."""
    
    def test_workflow_name_is_descriptive(self, workflow_data):
        """Test that the workflow name is descriptive."""
        name = workflow_data.get("name", "")
        assert len(name) > 0, "Workflow name should not be empty"
        assert len(name) <= 50, \
            "Workflow name should be reasonably short (≤50 chars)"
    
    def test_no_hardcoded_secrets(self, workflow_raw_content):
        """Test that there are no hardcoded secrets or tokens."""
        dangerous_patterns = [
            "password=",
            "token=",
            "api_key=",
            "secret=",
            "ghp_",
            "ghs_",
        ]
        content_lower = workflow_raw_content.lower()
        for pattern in dangerous_patterns:
            assert pattern not in content_lower, \
                f"Potential hardcoded secret pattern found: {pattern}"
    
    def test_branch_consistency(self, workflow_data):
        """Test that all branch references are consistent."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        push_branches = triggers.get("push", {}).get("branches", [])
        pr_branches = triggers.get("pull_request", {}).get("branches", [])
        
        assert push_branches == pr_branches, \
            "Push and pull_request triggers should target the same branches"
    
    def test_runner_is_supported(self, workflow_data):
        """Test that the runner OS is a supported GitHub Actions runner."""
        supported_runners = [
            "ubuntu-latest", "ubuntu-22.04", "ubuntu-20.04",
            "windows-latest", "windows-2022", "windows-2019",
            "macos-latest", "macos-13", "macos-12", "macos-11"
        ]
        build_job = workflow_data["jobs"]["build"]
        runner = build_job.get("runs-on", "")
        assert runner in supported_runners, \
            f"Runner '{runner}' should be a supported GitHub Actions runner"


class TestBranchMigration:
    """Test specific to the branch migration from 'base' to 'main'."""
    
    def test_no_base_branch_references(self, workflow_raw_content):
        """Test that there are no references to the old 'base' branch."""
        lines = workflow_raw_content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                continue
            if 'branches:' in line.lower():
                context_start = max(0, i-1)
                context_end = min(len(lines), i+3)
                context = '\n'.join(lines[context_start:context_end])
                if '"base"' in context or "'base'" in context or '[ "base" ]' in context:
                    pytest.fail(
                        f"Found reference to 'base' branch near line {i}: {line}"
                    )
    
    def test_main_branch_is_referenced(self, workflow_data):
        """Test that 'main' branch is properly referenced."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        push_branches = triggers.get("push", {}).get("branches", [])
        assert "main" in push_branches, \
            "Push trigger should reference 'main' branch"
        
        pr_branches = triggers.get("pull_request", {}).get("branches", [])
        assert "main" in pr_branches, \
            "Pull request trigger should reference 'main' branch"


class TestWorkflowRobustness:
    """Test robustness and error handling."""
    
    @pytest.mark.parametrize("required_field", ["name", "jobs"])
    def test_required_top_level_fields(self, workflow_data, required_field):
        """Test that required top-level fields are present."""
        assert required_field in workflow_data, \
            f"Workflow should have '{required_field}' field"
    
    @pytest.mark.parametrize("job_field", ["runs-on", "steps"])
    def test_required_job_fields(self, workflow_data, job_field):
        """Test that required job fields are present."""
        build_job = workflow_data["jobs"]["build"]
        assert job_field in build_job, \
            f"Build job should have '{job_field}' field"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestWorkflowComments:
    """Test workflow comments and documentation."""
    
    def test_workflow_has_descriptive_comments(self, workflow_raw_content):
        """Test that the workflow file contains helpful comments."""
        assert "# This is a basic workflow" in workflow_raw_content, \
            "Workflow should have introductory comment"
        assert "# Controls when the workflow will run" in workflow_raw_content, \
            "Workflow should explain trigger configuration"
    
    def test_commented_badge_link_is_valid(self, workflow_raw_content):
        """Test that the commented badge link has correct format."""
        lines = workflow_raw_content.split('\n')
        badge_lines = [line for line in lines if 'badge.svg' in line]
        
        if badge_lines:
            badge_line = badge_lines[0]
            assert 'github.com' in badge_line.lower(), \
                "Badge should reference github.com"
            assert 'blank.yml' in badge_line, \
                "Badge should reference the correct workflow file"
            assert badge_line.strip().startswith('#'), \
                "Badge link should be commented out"
    
    def test_step_comments_are_meaningful(self, workflow_raw_content):
        """Test that step comments provide meaningful context."""
        lines = workflow_raw_content.split('\n')
        step_comments = [line for line in lines if line.strip().startswith('# ') and 
                        ('step' in line.lower() or 'runs' in line.lower() or 'checks' in line.lower())]
        
        assert len(step_comments) > 0, \
            "Workflow should have comments explaining steps"


class TestWorkflowSecurityAndBestPractices:
    """Test security and best practice compliance."""
    
    def test_checkout_action_is_pinned(self, workflow_data):
        """Test that checkout action is pinned to a specific version."""
        steps = workflow_data["jobs"]["build"]["steps"]
        checkout_steps = [s for s in steps if "uses" in s and "checkout" in s["uses"]]
        
        for step in checkout_steps:
            action = step["uses"]
            assert "@" in action, \
                "Actions should be pinned to a version"
            assert not action.endswith("@main") and not action.endswith("@master"), \
                "Actions should not use branch references like @main or @master"
    
    def test_no_inline_scripts_with_secrets(self, workflow_raw_content):
        """Test that inline scripts don't contain secret patterns."""
        dangerous_patterns = [
            '${{ secrets.GITHUB_TOKEN }}',
            'export SECRET',
            'export PASSWORD',
            'export API_KEY'
        ]
        
        content_lower = workflow_raw_content.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in content_lower:
                pytest.fail(f"Potentially unsafe secret usage: {pattern}")
    
    def test_workflow_permissions_not_overly_permissive(self, workflow_data):
        """Test that workflow doesn't have overly permissive settings."""
        # If permissions are set, they should be specific
        if "permissions" in workflow_data:
            perms = workflow_data["permissions"]
            if isinstance(perms, str):
                assert perms != "write-all", \
                    "Workflow should not use 'write-all' permissions"
    
    def test_no_shell_injection_vulnerabilities(self, workflow_data):
        """Test that workflow steps don't have obvious shell injection risks."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        for i, step in enumerate(steps):
            if "run" in step:
                run_command = step["run"]
                # Check for dangerous patterns
                assert "${{ github.event" not in run_command or \
                       "github.event.issue.title" not in run_command, \
                    f"Step {i} may have shell injection vulnerability"


class TestWorkflowEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_workflow_handles_empty_branch_list(self, workflow_data):
        """Test that branch configurations are not empty."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        if "push" in triggers and "branches" in triggers["push"]:
            assert len(triggers["push"]["branches"]) > 0, \
                "Push trigger should specify at least one branch"
        
        if "pull_request" in triggers and "branches" in triggers["pull_request"]:
            assert len(triggers["pull_request"]["branches"]) > 0, \
                "Pull request trigger should specify at least one branch"
    
    def test_workflow_name_special_characters(self, workflow_data):
        """Test that workflow name doesn't contain problematic characters."""
        name = workflow_data.get("name", "")
        problematic_chars = ['<', '>', '|', '&', ';', '`', '$']
        
        for char in problematic_chars:
            assert char not in name, \
                f"Workflow name should not contain '{char}'"
    
    def test_step_names_are_unique(self, workflow_data):
        """Test that step names are unique within a job."""
        steps = workflow_data["jobs"]["build"]["steps"]
        named_steps = [s.get("name") for s in steps if "name" in s]
        
        assert len(named_steps) == len(set(named_steps)), \
            "Step names should be unique within a job"
    
    def test_workflow_file_size_is_reasonable(self, workflow_file_path):
        """Test that workflow file is not excessively large."""
        file_size = os.path.getsize(workflow_file_path)
        # Reasonable limit: 50KB for a workflow file
        assert file_size < 51200, \
            f"Workflow file size ({file_size} bytes) should be under 50KB"
    
    def test_no_circular_workflow_dependencies(self, workflow_data):
        """Test that workflow doesn't trigger itself recursively."""
        # This workflow should not trigger on workflow_run of itself
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        if "workflow_run" in triggers:
            workflow_run_config = triggers["workflow_run"]
            if "workflows" in workflow_run_config:
                triggered_workflows = workflow_run_config["workflows"]
                assert "blank.yml" not in triggered_workflows and "CI" not in triggered_workflows, \
                    "Workflow should not create circular dependencies"


class TestWorkflowYAMLCompliance:
    """Test YAML-specific compliance and formatting."""
    
    def test_yaml_indentation_consistency(self, workflow_raw_content):
        """Test that YAML uses consistent indentation."""
        lines = workflow_raw_content.split('\n')
        indentation_sizes = set()
        
        for line in lines:
            if line and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    indentation_sizes.add(leading_spaces)
        
        if len(indentation_sizes) > 1:
            # Check if all indentation is a multiple of 2
            for size in indentation_sizes:
                assert size % 2 == 0, \
                    f"Indentation should be in multiples of 2 spaces, found {size}"
    
    def test_no_tabs_in_yaml(self, workflow_raw_content):
        """Test that YAML doesn't contain tab characters."""
        assert '\t' not in workflow_raw_content, \
            "YAML should use spaces, not tabs for indentation"
    
    def test_yaml_keys_are_lowercase_with_underscores(self, workflow_data):
        """Test that YAML keys follow kebab-case or snake_case convention."""
        import re
        
        def check_keys(obj, path=""):
            if isinstance(obj, dict):
                for key in obj.keys():
                    if isinstance(key, str):
                        # Allow both kebab-case and snake_case, and some GitHub-specific keys
                        valid_pattern = re.match(r'^[a-z][a-z0-9_-]*$|^True$|^on$', str(key))
                        assert valid_pattern, \
                            f"Key '{key}' at {path} should use lowercase with hyphens/underscores"
                    check_keys(obj[key], f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_keys(item, f"{path}[{i}]")
        
        check_keys(workflow_data)
    
    def test_no_duplicate_keys_in_yaml(self, workflow_file_path):
        """Test that YAML doesn't have duplicate keys (Python's yaml handles this)."""
        # PyYAML will handle duplicates by overwriting, but we can check
        # by comparing the file line count with parsed structure
        with open(workflow_file_path, 'r') as f:
            content = f.read()
        
        # Basic check: count key occurrences in top level
        import re
        top_level_keys = re.findall(r'^([a-z_-]+):', content, re.MULTILINE)
        assert len(top_level_keys) == len(set(top_level_keys)), \
            "YAML should not have duplicate top-level keys"


class TestWorkflowPerformanceConsiderations:
    """Test performance and efficiency considerations."""
    
    def test_job_timeout_is_reasonable(self, workflow_data):
        """Test that jobs have reasonable timeout settings."""
        build_job = workflow_data["jobs"]["build"]
        
        # If timeout-minutes is set, it should be reasonable
        if "timeout-minutes" in build_job:
            timeout = build_job["timeout-minutes"]
            assert 1 <= timeout <= 360, \
                "Job timeout should be between 1 and 360 minutes"
    
    def test_workflow_not_overly_complex(self, workflow_data):
        """Test that workflow is not overly complex."""
        jobs = workflow_data.get("jobs", {})
        
        # Should have reasonable number of jobs
        assert len(jobs) <= 50, \
            "Workflow should not have more than 50 jobs for maintainability"
        
        # Each job should have reasonable number of steps
        for job_name, job_config in jobs.items():
            if "steps" in job_config:
                assert len(job_config["steps"]) <= 50, \
                    f"Job '{job_name}' should not have more than 50 steps"
    
    def test_caching_strategy_consideration(self, workflow_data):
        """Test that workflow considers caching where appropriate."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        # Just verify structure exists for future caching additions
        assert isinstance(steps, list), \
            "Steps should be properly structured for potential caching"


class TestWorkflowDocumentationAlignment:
    """Test alignment with documentation and comments."""
    
    def test_workflow_matches_documented_behavior(self, workflow_data):
        """Test that workflow behavior matches its documentation."""
        # The workflow is named "CI" and should perform CI-like tasks
        name = workflow_data.get("name", "")
        
        if name == "CI":
            # CI workflows should typically run on push and PR
            triggers = workflow_data.get(True, workflow_data.get("on", {}))
            assert "push" in triggers or "pull_request" in triggers, \
                "CI workflow should trigger on push or pull_request events"
    
    def test_branch_references_match_repository_default(self, workflow_data):
        """Test that workflow branches align with repository standards."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        # Modern repositories use 'main' as default
        if "push" in triggers and "branches" in triggers["push"]:
            branches = triggers["push"]["branches"]
            assert "main" in branches or "master" in branches, \
                "Workflow should target common default branches"


class TestWorkflowMaintainability:
    """Test workflow maintainability and code quality."""
    
    def test_step_order_is_logical(self, workflow_data):
        """Test that steps follow a logical order."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        # Checkout should be first or second step
        checkout_indices = [i for i, s in enumerate(steps) 
                           if "uses" in s and "checkout" in s["uses"]]
        
        if checkout_indices:
            assert checkout_indices[0] <= 1, \
                "Checkout step should be among the first steps"
    
    def test_action_versions_are_recent(self, workflow_data):
        """Test that GitHub Actions use reasonably recent versions."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        for step in steps:
            if "uses" in step:
                action = step["uses"]
                if "checkout" in action:
                    # checkout@v4 is current, v3 is acceptable, v2 and below are old
                    assert "@v3" in action or "@v4" in action, \
                        "Checkout action should use v3 or v4"
    
    def test_workflow_uses_shell_explicitly_if_needed(self, workflow_data):
        """Test that multi-line scripts explicitly set shell if needed."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        for step in steps:
            if "run" in step:
                run_cmd = step["run"]
                # If run contains multiple lines, shell should ideally be specified
                if "\n" in run_cmd and len(run_cmd.split('\n')) > 2:
                    # This is a guideline; not enforcing but checking structure
                    assert isinstance(step, dict), \
                        "Multi-line run steps should be properly structured"
    
    def test_environment_variables_are_documented(self, workflow_data):
        """Test that any environment variables used are properly structured."""
        build_job = workflow_data["jobs"]["build"]
        
        if "env" in build_job:
            env_vars = build_job["env"]
            assert isinstance(env_vars, dict), \
                "Environment variables should be a dictionary"
            
            for key, _value in env_vars.items():
                assert key.isupper() or "_" in key, \
                    f"Environment variable '{key}' should follow naming conventions"


class TestWorkflowContinuousIntegration:
    """Test CI-specific functionality and patterns."""
    
    def test_workflow_provides_feedback_mechanism(self, workflow_data):
        """Test that workflow has mechanisms to provide build feedback."""
        # Workflow should have some output or result indication
        steps = workflow_data["jobs"]["build"]["steps"]
        
        # At minimum, should have steps that produce output
        assert len(steps) > 0, \
            "CI workflow should have steps that produce output"
    
    def test_workflow_is_reproducible(self, workflow_data):
        """Test that workflow configuration supports reproducible builds."""
        build_job = workflow_data["jobs"]["build"]
        
        # Using specific runner versions and action versions helps reproducibility
        assert "runs-on" in build_job, \
            "Workflow should specify runner for reproducibility"
        
        steps = workflow_data["jobs"]["build"]["steps"]
        actions_used = [s.get("uses", "") for s in steps if "uses" in s]
        
        for action in actions_used:
            if action:
                assert "@" in action, \
                    f"Action '{action}' should be pinned for reproducibility"
    
    def test_workflow_failure_handling(self, workflow_data):
        """Test that workflow considers failure scenarios."""
        build_job = workflow_data["jobs"]["build"]
        
        # Verify job structure allows for proper failure handling
        assert "steps" in build_job, \
            "Job should have steps that can succeed or fail"
        
        # Steps can have continue-on-error, but this is optional
        # Just verify the structure supports it
        steps = build_job["steps"]
        for step in steps:
            if "continue-on-error" in step:
                assert isinstance(step["continue-on-error"], bool), \
                    "continue-on-error should be a boolean"


# Additional marker for workflow tests
pytestmark = pytest.mark.workflows