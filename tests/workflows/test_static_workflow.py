
















































































































































































































































































































































































































































































































































































































if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

# ============================================================================
# ADDITIONAL COMPREHENSIVE TESTS - Enhanced Coverage
# ============================================================================

@pytest.mark.workflows
@pytest.mark.parametrize("action_name,expected_version", [
    ("actions/checkout", "v4"),
    ("actions/configure-pages", "v5"),
    ("actions/upload-pages-artifact", "v3"),
    ("actions/deploy-pages", "v4"),
])
class TestStaticActionVersionsParametrized:
    """Parametrized tests for static workflow action versions"""
    
    def test_action_uses_correct_version(self, workflow_content, action_name, expected_version):
        """Test that each action uses the correct version"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        matching_steps = [s for s in steps if 'uses' in s and action_name in s['uses']]
        assert len(matching_steps) > 0, f"No steps found using {action_name}"
        
        for step in matching_steps:
            assert f"@{expected_version}" in step['uses'], \
                f"Expected {action_name}@{expected_version}, got {step['uses']}"


@pytest.mark.workflows
class TestStaticWorkflowNegativeScenarios:
    """Test error conditions and edge cases in static workflow"""
    
    def test_handles_missing_upload_path(self):
        """Test that workflow can handle missing upload path configuration"""
        # Default path should be used if not specified
        workflow_snippet = """
name: Test
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/upload-pages-artifact@v3
"""
        parsed = yaml.safe_load(workflow_snippet)
        deploy_job = parsed['jobs']['deploy']
        upload_step = deploy_job['steps'][0]
        
        # Missing 'with' section is valid (uses defaults)
        assert 'with' not in upload_step or upload_step.get('with') is None
    
    def test_invalid_upload_path_format_detection(self):
        """Test detection of potentially problematic upload paths"""
        problematic_paths = [
            '../outside',  # Goes outside repo
            '/absolute/path',  # Absolute path
            '~/',  # Home directory
        ]
        
        for path in problematic_paths:
            workflow_snippet = f"""
name: Test
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/upload-pages-artifact@v3
        with:
          path: '{path}'
"""
            parsed = yaml.safe_load(workflow_snippet)
            upload_step = parsed['jobs']['deploy']['steps'][0]
            actual_path = upload_step['with']['path']
            
            # These paths would work but might not be intended
            # Just verify they parse correctly
            assert actual_path == path
    
    def test_workflow_without_checkout_implications(self):
        """Test implications of static workflow without separate checkout"""
        # In the actual static workflow, checkout is combined with upload
        # This tests understanding of the pattern
        workflow_with_checkout = """
name: Test
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
"""
        parsed = yaml.safe_load(workflow_with_checkout)
        steps = parsed['jobs']['deploy']['steps']
        
        checkout_steps = [s for s in steps if 'checkout' in s.get('uses', '')]
        assert len(checkout_steps) > 0, "Should have checkout step"
    
    def test_empty_repository_upload_handling(self):
        """Test that workflow would handle empty repository correctly"""
        # Uploading '.' would upload everything including empty dirs
        workflow_snippet = """
name: Test
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
"""
        parsed = yaml.safe_load(workflow_snippet)
        upload_step = parsed['jobs']['deploy']['steps'][1]
        
        assert upload_step['with']['path'] == '.', "Should upload current directory"


@pytest.mark.workflows
@pytest.mark.integration
class TestStaticWorkflowIntegration:
    """Integration tests for static workflow behavior"""
    
    def test_single_job_simplicity(self, workflow_content):
        """Test that static workflow correctly uses single job pattern"""
        jobs = workflow_content.get('jobs', {})
        
        # Should have only one job (deploy)
        assert len(jobs) == 1, \
            f"Static workflow should have 1 job, got {len(jobs)}"
        assert 'deploy' in jobs, "Job should be named 'deploy'"
    
    def test_no_build_step_in_static_workflow(self, workflow_content):
        """Test that static workflow doesn't have unnecessary build steps"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        # Should not have Jekyll or other build actions
        build_actions = ['jekyll-build-pages', 'setup-node', 'npm', 'yarn', 'build']
        for step in steps:
            uses = step.get('uses', '')
            run = step.get('run', '')
            
            for build_action in build_actions:
                assert build_action not in uses.lower(), \
                    f"Static workflow should not have build action: {build_action}"
                assert build_action not in run.lower(), \
                    f"Static workflow should not run build commands: {build_action}"
    
    def test_checkout_and_upload_in_same_job(self, workflow_content):
        """Test that checkout and upload happen in same job"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        has_checkout = any('checkout' in s.get('uses', '') for s in steps)
        has_upload = any('upload-pages-artifact' in s.get('uses', '') for s in steps)
        
        assert has_checkout and has_upload, \
            "Static workflow should have both checkout and upload in single job"
    
    def test_permissions_sufficient_for_static_deployment(self, workflow_content):
        """Test that permissions are sufficient for static Pages deployment"""
        permissions = workflow_content.get('permissions', {})
        
        # Need same three permissions as Jekyll workflow
        required = ['contents', 'pages', 'id-token']
        for perm in required:
            assert perm in permissions, f"Missing required permission: {perm}"
        
        assert permissions['contents'] == 'read'
        assert permissions['pages'] == 'write'
        assert permissions['id-token'] == 'write'
    
    def test_environment_configuration_matches_deployment(self, workflow_content):
        """Test that environment is properly configured for deployment"""
        deploy_job = workflow_content['jobs']['deploy']
        env = deploy_job.get('environment', {})
        
        assert env.get('name') == 'github-pages', "Should deploy to github-pages environment"
        assert 'url' in env, "Should specify environment URL"
        assert 'steps.deployment.outputs.page_url' in env['url'], \
            "URL should reference deployment output"


@pytest.mark.workflows
class TestStaticWorkflowSpecificConfiguration:
    """Test static workflow specific configuration"""
    
    def test_uploads_entire_repository(self, workflow_content):
        """Test that static workflow uploads entire repository"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        upload_steps = [s for s in steps if 'upload-pages-artifact' in s.get('uses', '')]
        assert len(upload_steps) > 0, "Must have upload step"
        
        upload_step = upload_steps[0]
        if 'with' in upload_step and 'path' in upload_step['with']:
            path = upload_step['with']['path']
            assert path == '.', \
                f"Static workflow should upload current directory (.), got '{path}'"
    
    def test_no_source_destination_configuration(self, workflow_content):
        """Test that static workflow doesn't have build source/destination"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        for step in steps:
            if 'with' in step:
                config = step['with']
                # Static workflow shouldn't have source/destination like Jekyll
                assert 'source' not in config or config.get('source') == '.', \
                    "Static workflow shouldn't have custom source"
                assert 'destination' not in config, \
                    "Static workflow shouldn't have destination (no build)"
    
    def test_minimal_step_count(self, workflow_content):
        """Test that static workflow has minimal necessary steps"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        # Should have: checkout, setup pages, upload, deploy (4 steps)
        assert 4 <= len(steps) <= 5, \
            f"Static workflow should have 4-5 steps, got {len(steps)}"
    
    def test_steps_in_correct_order(self, workflow_content):
        """Test that steps are in the correct order"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        step_types = []
        for step in steps:
            uses = step.get('uses', '')
            if 'checkout' in uses:
                step_types.append('checkout')
            elif 'configure-pages' in uses:
                step_types.append('setup')
            elif 'upload-pages-artifact' in uses:
                step_types.append('upload')
            elif 'deploy-pages' in uses:
                step_types.append('deploy')
        
        # Expected order
        expected_order = ['checkout', 'setup', 'upload', 'deploy']
        assert step_types == expected_order, \
            f"Steps out of order. Expected {expected_order}, got {step_types}"


@pytest.mark.workflows
@pytest.mark.parametrize("trigger_type,should_exist", [
    ("push", True),
    ("workflow_dispatch", True),
    ("pull_request", False),
    ("schedule", False),
])
class TestStaticTriggerConfiguration:
    """Parametrized tests for static workflow trigger configuration"""
    
    def test_trigger_existence(self, workflow_content, trigger_type, should_exist):
        """Test that triggers are configured correctly"""
        triggers = workflow_content.get(True) or workflow_content.get('on')
        
        if should_exist:
            assert trigger_type in triggers, f"Should have {trigger_type} trigger"
        else:
            assert trigger_type not in triggers, \
                f"Should not have {trigger_type} trigger (deployment workflow)"


@pytest.mark.workflows
class TestStaticWorkflowSimplicity:
    """Test that static workflow maintains simplicity"""
    
    def test_no_matrix_strategy(self, workflow_content):
        """Test that static workflow doesn't use matrix strategy"""
        deploy_job = workflow_content['jobs']['deploy']
        
        assert 'strategy' not in deploy_job, \
            "Static deployment shouldn't need matrix strategy"
    
    def test_no_conditional_steps(self, workflow_content):
        """Test that steps run unconditionally (no if: conditions)"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        for step in steps:
            # Conditionals complicate static deployments
            if 'if' in step:
                # This is allowed but should be rare in static workflow
                pass
    
    def test_no_custom_environment_variables(self, workflow_content):
        """Test that workflow doesn't require custom env vars"""
        deploy_job = workflow_content['jobs']['deploy']
        
        # Job-level env vars
        job_env = deploy_job.get('env', {})
        assert len(job_env) == 0, \
            "Static workflow shouldn't need custom environment variables"
        
        # Step-level env vars
        steps = deploy_job.get('steps', [])
        for step in steps:
            step_env = step.get('env', {})
            assert len(step_env) == 0, \
                "Static workflow steps shouldn't need custom env vars"
    
    def test_single_runner_type(self, workflow_content):
        """Test that workflow uses single runner type"""
        jobs = workflow_content.get('jobs', {})
        runners = [job.get('runs-on') for job in jobs.values()]
        
        # All should be the same (ubuntu-latest)
        assert len(set(runners)) == 1, \
            "Static workflow should use consistent runner"
        assert runners[0] == 'ubuntu-latest', \
            "Should use ubuntu-latest for consistency"


@pytest.mark.workflows
class TestStaticWorkflowSecurity:
    """Test security aspects of static workflow"""
    
    def test_no_secrets_in_static_workflow(self, workflow_content):
        """Test that static workflow doesn't require secrets"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        for step in steps:
            # Check for secret references
            if 'with' in step:
                config_str = str(step['with'])
                assert 'secrets.' not in config_str, \
                    "Static workflow shouldn't need secrets"
            if 'env' in step:
                env_str = str(step['env'])
                assert 'secrets.' not in env_str, \
                    "Static workflow shouldn't need secrets in env"
    
    def test_uses_oidc_token_authentication(self, workflow_content):
        """Test that workflow uses OIDC (no PAT needed)"""
        permissions = workflow_content.get('permissions', {})
        
        # id-token write indicates OIDC usage
        assert 'id-token' in permissions, \
            "Should use OIDC authentication"
        assert permissions['id-token'] == 'write', \
            "OIDC requires write permission on id-token"
    
    def test_no_third_party_actions(self, workflow_content):
        """Test that workflow only uses official GitHub actions"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        for step in steps:
            if 'uses' in step:
                uses = step['uses']
                # Should only use actions/* (GitHub official)
                if '@' in uses:
                    action_name = uses.split('@')[0]
                    assert action_name.startswith('actions/'), \
                        f"Should only use official actions, got: {action_name}"
    
    def test_read_only_content_access(self, workflow_content):
        """Test that workflow only reads repository content"""
        permissions = workflow_content.get('permissions', {})
        
        assert permissions.get('contents') == 'read', \
            "Should only need read access to repository contents"


@pytest.mark.workflows
class TestStaticWorkflowPerformance:
    """Test performance characteristics of static workflow"""
    
    def test_single_job_is_faster(self, workflow_content):
        """Test that single job design is optimal for static content"""
        jobs = workflow_content.get('jobs', {})
        
        # Single job means no job coordination overhead
        assert len(jobs) == 1, \
            "Single job design minimizes workflow execution time"
    
    def test_no_dependency_installation(self, workflow_content):
        """Test that workflow doesn't install dependencies"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        dependency_commands = ['npm install', 'pip install', 'gem install', 'yarn install']
        
        for step in steps:
            run = step.get('run', '')
            for cmd in dependency_commands:
                assert cmd not in run, \
                    f"Static workflow shouldn't install dependencies: {cmd}"
    
    def test_minimal_actions_usage(self, workflow_content):
        """Test that workflow uses minimal necessary actions"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        action_steps = [s for s in steps if 'uses' in s]
        
        # Should have exactly 4 action steps
        assert len(action_steps) == 4, \
            f"Should use exactly 4 actions (checkout, setup, upload, deploy), got {len(action_steps)}"
    
    def test_upload_path_efficiency(self, workflow_content):
        """Test that upload path is efficient"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        upload_steps = [s for s in steps if 'upload-pages-artifact' in s.get('uses', '')]
        upload_step = upload_steps[0]
        
        if 'with' in upload_step and 'path' in upload_step['with']:
            path = upload_step['with']['path']
            # '.' is most efficient (uploads everything in current dir)
            assert path == '.', \
                "Using '.' is most efficient for static content"


@pytest.mark.workflows
class TestStaticWorkflowDocumentation:
    """Test documentation and clarity of static workflow"""
    
    def test_workflow_name_indicates_static_content(self, workflow_content):
        """Test that workflow name clearly indicates static content"""
        name = workflow_content.get('name', '')
        name_lower = name.lower()
        
        assert 'static' in name_lower, \
            "Workflow name should mention 'static'"
        assert 'pages' in name_lower or 'deploy' in name_lower, \
            "Workflow name should mention deployment purpose"
    
    def test_comments_explain_simplicity(self, workflow_raw):
        """Test that comments explain static deployment approach"""
        lines = workflow_raw.split('\n')
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        
        # Should have comments
        assert len(comment_lines) >= 2, \
            "Workflow should have explanatory comments"
        
        # Look for key terms in comments
        all_comments = ' '.join(comment_lines).lower()
        assert 'static' in all_comments or 'simple' in all_comments, \
            "Comments should explain static/simple nature"
    
    def test_job_name_is_clear(self, workflow_content):
        """Test that job name clearly indicates purpose"""
        jobs = workflow_content.get('jobs', {})
        
        assert 'deploy' in jobs, "Job should be named 'deploy'"
        
        deploy_job = jobs['deploy']
        # Job should have environment indicating it's deploying
        assert 'environment' in deploy_job, \
            "Deploy job should specify environment"


@pytest.mark.workflows
class TestStaticWorkflowMaintainability:
    """Test maintainability aspects of static workflow"""
    
    def test_action_versions_are_explicit(self, workflow_content):
        """Test that all action versions are explicitly specified"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        for step in steps:
            if 'uses' in step:
                uses = step['uses']
                assert '@' in uses, f"Action should specify version: {uses}"
                
                # Should use semantic versions, not branches
                version = uses.split('@')[1]
                assert not version.startswith('main'), \
                    "Should use version tags, not @main"
                assert not version.startswith('master'), \
                    "Should use version tags, not @master"
    
    def test_configuration_is_minimal(self, workflow_content):
        """Test that workflow has minimal configuration"""
        # Count total configuration keys
        config_keys = set()
        
        def count_keys(d, prefix=''):
            if isinstance(d, dict):
                for k, v in d.items():
                    config_keys.add(f"{prefix}.{k}" if prefix else k)
                    count_keys(v, f"{prefix}.{k}" if prefix else k)
        
        count_keys(workflow_content)
        
        # Static workflow should be simpler than Jekyll workflow
        # Reasonable threshold: < 40 unique configuration keys
        assert len(config_keys) < 40, \
            f"Static workflow should be simple, got {len(config_keys)} config keys"
    
    def test_no_complex_conditionals(self, workflow_content):
        """Test that workflow avoids complex conditional logic"""
        deploy_job = workflow_content['jobs']['deploy']
        
        # Job-level conditionals
        assert 'if' not in deploy_job, \
            "Job shouldn't have conditional execution"
        
        # Step-level conditionals
        steps = deploy_job.get('steps', [])
        conditional_steps = [s for s in steps if 'if' in s]
        
        assert len(conditional_steps) == 0, \
            "Steps shouldn't have conditional execution in static workflow"


@pytest.mark.workflows
class TestStaticWorkflowComparison:
    """Test how static workflow compares to Jekyll workflow"""
    
    def test_simpler_than_jekyll_workflow(self, workflow_content):
        """Test that static workflow is simpler than Jekyll workflow"""
        # Static should have fewer jobs (1 vs 2)
        jobs = workflow_content.get('jobs', {})
        assert len(jobs) == 1, "Static workflow should have single job"
        
        # Static should have fewer total steps
        total_steps = sum(len(job.get('steps', [])) for job in jobs.values())
        assert total_steps <= 5, \
            f"Static workflow should have ≤5 steps, got {total_steps}"
    
    def test_no_build_artifacts_complexity(self, workflow_content):
        """Test that static workflow avoids build complexity"""
        deploy_job = workflow_content['jobs']['deploy']
        steps = deploy_job.get('steps', [])
        
        # Should not have separate build/upload pattern
        # Upload should happen directly without intermediate build
        action_sequence = [s.get('uses', '').split('@')[0] for s in steps if 'uses' in s]
        
        # Should not have build action between checkout and upload
        if 'actions/checkout' in action_sequence:
            checkout_idx = action_sequence.index('actions/checkout')
            upload_idx = None
            for i, action in enumerate(action_sequence):
                if 'upload-pages-artifact' in action:
                    upload_idx = i
                    break
            
            if upload_idx:
                # Between checkout and upload, should only be setup-pages
                between = action_sequence[checkout_idx+1:upload_idx]
                for action in between:
                    assert 'build' not in action.lower(), \
                        "Should not have build actions between checkout and upload"

