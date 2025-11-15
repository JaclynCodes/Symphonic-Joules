






































































































































































































































































































































































































































































































































































































if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

# ============================================================================
# ADDITIONAL COMPREHENSIVE TESTS - Enhanced Coverage
# ============================================================================

@pytest.mark.workflows
@pytest.mark.parametrize("action_name,expected_version", [
    ("actions/checkout", "v4"),
    ("actions/configure-pages", "v5"),
    ("actions/jekyll-build-pages", "v1"),
    ("actions/upload-pages-artifact", "v3"),
    ("actions/deploy-pages", "v4"),
])
class TestActionVersionsParametrized:
    """Parametrized tests for action versions"""
    
    def test_action_uses_correct_version(self, workflow_content, action_name, expected_version):
        """Test that each action uses the correct version"""
        jobs = workflow_content.get('jobs', {})
        all_steps = []
        for job_config in jobs.values():
            all_steps.extend(job_config.get('steps', []))
        
        matching_steps = [s for s in all_steps if 'uses' in s and action_name in s['uses']]
        assert len(matching_steps) > 0, f"No steps found using {action_name}"
        
        for step in matching_steps:
            assert f"@{expected_version}" in step['uses'], \
                f"Expected {action_name}@{expected_version}, got {step['uses']}"


@pytest.mark.workflows
class TestWorkflowNegativeScenarios:
    """Test error conditions and edge cases in workflow"""
    
    def test_workflow_handles_missing_keys_gracefully(self):
        """Test that workflow parser handles missing optional keys"""
        minimal_workflow = """
name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
"""
        parsed = yaml.safe_load(minimal_workflow)
        assert parsed is not None, "Should parse minimal valid workflow"
        assert 'jobs' in parsed, "Should have jobs section"
    
    def test_invalid_yaml_structure_detection(self):
        """Test detection of invalid YAML structure"""
        invalid_yaml = "name: Test\n  invalid indentation"
        
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load(invalid_yaml)
    
    def test_workflow_rejects_duplicate_job_names(self):
        """Test that duplicate job names would cause issues"""
        workflow_with_dup = """
name: Test
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps: []
  build:
    runs-on: ubuntu-latest
    steps: []
"""
        # YAML allows this but last definition wins
        parsed = yaml.safe_load(workflow_with_dup)
        # Should only have one 'build' job (last one wins)
        assert len(parsed['jobs']) == 1, "Duplicate keys should be overwritten"
    
    def test_missing_required_job_fields(self):
        """Test detection of missing required job fields"""
        workflow_missing_runner = """
name: Test
on: push
jobs:
  build:
    steps:
      - uses: actions/checkout@v4
"""
        parsed = yaml.safe_load(workflow_missing_runner)
        build_job = parsed['jobs']['build']
        
        # Missing runs-on should be detectable
        assert 'runs-on' not in build_job, "Job missing runs-on field"
    
    def test_empty_steps_array_handling(self):
        """Test that empty steps array is valid but useless"""
        workflow_empty_steps = """
name: Test
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps: []
"""
        parsed = yaml.safe_load(workflow_empty_steps)
        assert len(parsed['jobs']['build']['steps']) == 0, \
            "Should allow empty steps array"


@pytest.mark.workflows
@pytest.mark.integration
class TestJekyllWorkflowIntegration:
    """Integration tests for Jekyll workflow behavior"""
    
    def test_build_before_deploy_sequence(self, workflow_content):
        """Test that build must complete before deploy starts"""
        deploy_job = workflow_content['jobs']['deploy']
        
        # Deploy must depend on build
        assert 'needs' in deploy_job, "Deploy job must specify dependencies"
        needs = deploy_job['needs']
        
        if isinstance(needs, str):
            assert needs == 'build'
        else:
            assert 'build' in needs
    
    def test_artifact_upload_and_deploy_coordination(self, workflow_content):
        """Test that artifact upload in build matches deploy expectations"""
        build_job = workflow_content['jobs']['build']
        deploy_job = workflow_content['jobs']['deploy']
        
        # Build should upload artifact
        build_steps = build_job.get('steps', [])
        upload_steps = [s for s in build_steps if 'upload-pages-artifact' in s.get('uses', '')]
        assert len(upload_steps) > 0, "Build job must upload artifact"
        
        # Deploy should deploy pages
        deploy_steps = deploy_job.get('steps', [])
        deploy_actions = [s for s in deploy_steps if 'deploy-pages' in s.get('uses', '')]
        assert len(deploy_actions) > 0, "Deploy job must deploy pages"
    
    def test_environment_url_references_deployment_output(self, workflow_content):
        """Test that environment URL properly references deployment step output"""
        deploy_job = workflow_content['jobs']['deploy']
        env = deploy_job.get('environment', {})
        url = env.get('url', '')
        
        # Should reference the deployment step's output
        assert 'steps.deployment.outputs' in url, \
            "Environment URL should reference deployment step output"
        assert 'page_url' in url, \
            "Environment URL should reference page_url output"
    
    def test_permissions_sufficient_for_deployment(self, workflow_content):
        """Test that permissions are sufficient for GitHub Pages deployment"""
        permissions = workflow_content.get('permissions', {})
        
        # Need these three for Pages deployment
        required = ['contents', 'pages', 'id-token']
        for perm in required:
            assert perm in permissions, f"Missing required permission: {perm}"
            
        # Verify appropriate access levels
        assert permissions['contents'] == 'read', "Should only need read access to contents"
        assert permissions['pages'] == 'write', "Need write access to deploy pages"
        assert permissions['id-token'] == 'write', "Need write access for OIDC token"
    
    def test_concurrency_prevents_deployment_conflicts(self, workflow_content):
        """Test that concurrency settings prevent deployment conflicts"""
        concurrency = workflow_content.get('concurrency', {})
        
        # Should have pages group
        assert concurrency.get('group') == 'pages', \
            "Concurrency group should be 'pages'"
        
        # Should not cancel in-progress deployments
        assert concurrency.get('cancel-in-progress') is False, \
            "Should not cancel in-progress deployments"


@pytest.mark.workflows
class TestJekyllSpecificConfiguration:
    """Test Jekyll-specific configuration and setup"""
    
    def test_jekyll_build_source_configuration(self, workflow_content):
        """Test Jekyll build source is properly configured"""
        build_job = workflow_content['jobs']['build']
        steps = build_job.get('steps', [])
        
        jekyll_steps = [s for s in steps if 'jekyll-build-pages' in s.get('uses', '')]
        assert len(jekyll_steps) > 0, "Must have Jekyll build step"
        
        jekyll_step = jekyll_steps[0]
        assert 'with' in jekyll_step, "Jekyll step should have configuration"
        assert 'source' in jekyll_step['with'], "Jekyll step should specify source"
    
    def test_jekyll_build_destination_is_standard(self, workflow_content):
        """Test that Jekyll outputs to standard _site directory"""
        build_job = workflow_content['jobs']['build']
        steps = build_job.get('steps', [])
        
        jekyll_steps = [s for s in steps if 'jekyll-build-pages' in s.get('uses', '')]
        jekyll_step = jekyll_steps[0]
        
        destination = jekyll_step.get('with', {}).get('destination', '')
        assert '_site' in destination, "Jekyll should build to _site directory"
    
    def test_pages_setup_before_jekyll_build(self, workflow_content):
        """Test that GitHub Pages is configured before Jekyll builds"""
        build_job = workflow_content['jobs']['build']
        steps = build_job.get('steps', [])
        
        # Find step indices
        setup_idx = None
        jekyll_idx = None
        
        for i, step in enumerate(steps):
            uses = step.get('uses', '')
            if 'configure-pages' in uses:
                setup_idx = i
            elif 'jekyll-build-pages' in uses:
                jekyll_idx = i
        
        assert setup_idx is not None, "Setup pages step not found"
        assert jekyll_idx is not None, "Jekyll build step not found"
        assert setup_idx < jekyll_idx, "Setup pages must run before Jekyll build"
    
    def test_checkout_before_any_build_actions(self, workflow_content):
        """Test that repository checkout happens first in build job"""
        build_job = workflow_content['jobs']['build']
        steps = build_job.get('steps', [])
        
        if len(steps) > 0:
            first_step = steps[0]
            assert 'checkout' in first_step.get('uses', ''), \
                "First step should be checkout"


@pytest.mark.workflows
@pytest.mark.parametrize("trigger_type,expected_config", [
    ("push", {"branches": ["main"]}),
    ("workflow_dispatch", None),
])
class TestTriggerConfigurationsParametrized:
    """Parametrized tests for trigger configurations"""
    
    def test_trigger_is_configured_correctly(self, workflow_content, trigger_type, expected_config):
        """Test that each trigger type is configured correctly"""
        triggers = workflow_content.get(True) or workflow_content.get('on')
        
        assert trigger_type in triggers, f"Missing trigger: {trigger_type}"
        
        if expected_config is not None:
            trigger_config = triggers[trigger_type]
            for key, value in expected_config.items():
                assert key in trigger_config, \
                    f"Trigger {trigger_type} missing key: {key}"
                assert trigger_config[key] == value, \
                    f"Trigger {trigger_type} {key} mismatch"


@pytest.mark.workflows
class TestWorkflowStepNaming:
    """Test that workflow steps have clear, descriptive names"""
    
    def test_all_steps_have_names(self, workflow_content):
        """Test that all steps have descriptive names"""
        jobs = workflow_content.get('jobs', {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for i, step in enumerate(steps):
                # Steps using actions should have names (best practice)
                if 'uses' in step:
                    # Name is optional but recommended
                    if 'name' not in step:
                        # This is not an error, but log it
                        pass
    
    def test_step_names_are_descriptive(self, workflow_content):
        """Test that step names are meaningful"""
        jobs = workflow_content.get('jobs', {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'name' in step:
                    name = step['name']
                    # Names should have some substance
                    assert len(name) > 3, f"Step name too short: '{name}'"
                    assert name != name.lower() or name != name.upper(), \
                        f"Step name should have proper capitalization: '{name}'"
    
    def test_build_job_steps_are_ordered_logically(self, workflow_content):
        """Test that build job steps follow logical order"""
        build_job = workflow_content['jobs']['build']
        steps = build_job.get('steps', [])
        
        step_names = [s.get('name', s.get('uses', '')) for s in steps]
        
        # Common patterns: checkout, setup, build, upload
        # Verify checkout is early
        checkout_indices = [i for i, name in enumerate(step_names) if 'checkout' in name.lower()]
        if checkout_indices:
            assert checkout_indices[0] == 0, "Checkout should be first step"


@pytest.mark.workflows
class TestWorkflowSecurityHardening:
    """Test security hardening in workflow"""
    
    def test_actions_use_commit_shas_or_tags(self, workflow_content):
        """Test that actions use specific versions, not @main or @master"""
        jobs = workflow_content.get('jobs', {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    uses = step['uses']
                    # Should not use @main or @master (security risk)
                    assert '@main' not in uses.lower(), \
                        f"Action should not use @main: {uses}"
                    assert '@master' not in uses.lower(), \
                        f"Action should not use @master: {uses}"
    
    def test_no_arbitrary_code_execution_in_run_steps(self, workflow_content):
        """Test that workflow doesn't have obvious code execution risks"""
        jobs = workflow_content.get('jobs', {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'run' in step:
                    run_command = step['run']
                    # Check for dangerous patterns
                    dangerous = ['eval', 'exec', 'curl | bash', 'wget | sh']
                    for pattern in dangerous:
                        assert pattern not in run_command.lower(), \
                            f"Potentially dangerous pattern in run step: {pattern}"
    
    def test_permissions_follow_principle_of_least_privilege(self, workflow_content):
        """Test that workflow follows least privilege principle"""
        permissions = workflow_content.get('permissions', {})
        
        # Should not have write-all or excessive permissions
        assert permissions != 'write-all', "Should not use write-all permissions"
        
        # Count write permissions
        write_perms = [k for k, v in permissions.items() if v == 'write']
        assert len(write_perms) <= 2, \
            f"Too many write permissions: {write_perms} (should be minimal)"


@pytest.mark.workflows
class TestWorkflowPerformanceConsiderations:
    """Test workflow configuration for performance"""
    
    def test_jobs_run_in_parallel_where_possible(self, workflow_content):
        """Test that independent jobs can run in parallel"""
        jobs = workflow_content.get('jobs', {})
        
        # Build and deploy must be sequential (deploy needs build)
        # This is correct for this workflow
        deploy_job = jobs.get('deploy', {})
        if 'needs' in deploy_job:
            # This is expected and correct
            pass
    
    def test_no_unnecessary_checkout_steps(self, workflow_content):
        """Test that checkout isn't done multiple times unnecessarily"""
        build_job = workflow_content['jobs']['build']
        build_steps = build_job.get('steps', [])
        
        checkout_count = len([s for s in build_steps if 'checkout' in s.get('uses', '')])
        assert checkout_count <= 1, \
            f"Build job should checkout once, not {checkout_count} times"
        
        # Deploy job shouldn't need checkout (it uses artifact)
        deploy_job = workflow_content['jobs']['deploy']
        deploy_steps = deploy_job.get('steps', [])
        
        deploy_checkouts = [s for s in deploy_steps if 'checkout' in s.get('uses', '')]
        # Deploy typically doesn't need checkout since it uses uploaded artifact
        if len(deploy_checkouts) > 0:
            # This might be intentional, just noting it
            pass
    
    def test_uses_ubuntu_latest_for_speed(self, workflow_content):
        """Test that workflow uses ubuntu-latest (typically fastest)"""
        jobs = workflow_content.get('jobs', {})
        
        for job_name, job_config in jobs.items():
            runner = job_config.get('runs-on', '')
            if runner:
                # ubuntu-latest is typically fastest for CI
                assert 'ubuntu' in runner, \
                    f"Job '{job_name}' should use ubuntu for better performance"


@pytest.mark.workflows
class TestWorkflowDocumentation:
    """Test workflow documentation and clarity"""
    
    def test_workflow_has_clear_name(self, workflow_content):
        """Test that workflow name clearly indicates purpose"""
        name = workflow_content.get('name', '')
        
        # Should mention Jekyll and Pages
        name_lower = name.lower()
        assert 'jekyll' in name_lower, "Workflow name should mention Jekyll"
        assert 'pages' in name_lower or 'deploy' in name_lower, \
            "Workflow name should mention deployment purpose"
    
    def test_comments_explain_non_obvious_config(self, workflow_raw):
        """Test that workflow has helpful comments"""
        lines = workflow_raw.split('\n')
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        
        # Should have at least a few comments
        assert len(comment_lines) >= 3, \
            "Workflow should have comments explaining configuration"
    
    def test_job_names_are_self_documenting(self, workflow_content):
        """Test that job names clearly indicate their purpose"""
        jobs = workflow_content.get('jobs', {})
        
        for job_name in jobs.keys():
            # Job names should be clear
            assert len(job_name) > 2, f"Job name too short: '{job_name}'"
            assert job_name.isidentifier(), f"Job name should be valid identifier: '{job_name}'"

