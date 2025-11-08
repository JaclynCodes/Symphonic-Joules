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