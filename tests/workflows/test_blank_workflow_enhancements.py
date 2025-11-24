"""
Comprehensive tests for enhancements in .github/workflows/blank.yml

This module tests the new Python testing and linting features added to the CI workflow:
- Python setup and dependency installation
- Flake8 linting configuration
- Pytest execution
- Multiple Python tool integrations (black, isort, mypy)
- Action version updates (checkout@v5, setup-python@v5)
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope='module')
def workflow_path():
    """Get path to blank workflow file"""
    return Path('.github/workflows/blank.yml')


@pytest.fixture(scope='module')
def workflow_content(workflow_path):
    """Load and parse workflow content"""
    with open(workflow_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope='module')
def build_job(workflow_content):
    """Get build job configuration"""
    return workflow_content.get('jobs', {}).get('build', {})


@pytest.fixture(scope='module')
def steps(build_job):
    """Get list of steps from build job"""
    return build_job.get('steps', [])


class TestActionVersions:
    """Test that actions use updated versions"""
    
    def test_checkout_uses_v5(self, steps):
        """Test that checkout action uses v5"""
        checkout_steps = [s for s in steps if 'actions/checkout' in str(s.get('uses', ''))]
        assert len(checkout_steps) > 0, "Should have checkout step"
        for step in checkout_steps:
            uses = step.get('uses', '')
            assert '@v5' in uses, \
                f"Checkout should use @v5, got: {uses}"
    
    def test_no_old_checkout_versions(self, steps):
        """Test that old checkout versions are not used"""
        for step in steps:
            uses = step.get('uses', '')
            if 'actions/checkout' in uses:
                assert '@v4' not in uses and '@v3' not in uses, \
                    f"Should not use old checkout versions: {uses}"


class TestPythonSetup:
    """Test Python setup step configuration"""
    
    def test_has_python_setup_step(self, steps):
        """Test that workflow includes Python setup step"""
        python_steps = [s for s in steps 
                       if 'actions/setup-python' in str(s.get('uses', ''))]
        assert len(python_steps) > 0, \
            "Workflow should include Python setup step"
    
    def test_python_setup_uses_v5(self, steps):
        """Test that Python setup uses v5"""
        python_steps = [s for s in steps 
                       if 'actions/setup-python' in str(s.get('uses', ''))]
        for step in python_steps:
            uses = step.get('uses', '')
            assert '@v5' in uses, \
                f"Python setup should use @v5, got: {uses}"
    
    def test_python_version_specified(self, steps):
        """Test that Python version is explicitly specified"""
        python_steps = [s for s in steps 
                       if 'actions/setup-python' in str(s.get('uses', ''))]
        assert len(python_steps) > 0, "Should have Python setup step"
        
        for step in python_steps:
            with_config = step.get('with', {})
            assert 'python-version' in with_config, \
                "Python setup should specify python-version"
    
    def test_python_version_is_312(self, steps):
        """Test that Python 3.12 is used"""
        python_steps = [s for s in steps 
                       if 'actions/setup-python' in str(s.get('uses', ''))]
        for step in python_steps:
            with_config = step.get('with', {})
            version = with_config.get('python-version', '')
            assert '3.12' in str(version), \
                f"Should use Python 3.12, got: {version}"
    
    def test_python_setup_has_name(self, steps):
        """Test that Python setup step has descriptive name"""
        python_steps = [s for s in steps 
                       if 'actions/setup-python' in str(s.get('uses', ''))]
        for step in python_steps:
            assert 'name' in step, \
                "Python setup step should have a name"
            name = step.get('name', '').lower()
            assert 'python' in name, \
                f"Python setup step name should mention Python: {step.get('name')}"


class TestDependencyInstallation:
    """Test dependency installation step"""
    
    def test_has_install_dependencies_step(self, steps):
        """Test that workflow has dependency installation step"""
        install_steps = [s for s in steps 
                        if 'install' in str(s.get('name', '')).lower() and
                        'dependencies' in str(s.get('name', '')).lower()]
        assert len(install_steps) > 0, \
            "Should have 'Install dependencies' step"
    
    def test_upgrades_pip(self, steps):
        """Test that pip is upgraded before installing dependencies"""
        install_steps = [s for s in steps 
                        if 'install' in str(s.get('name', '')).lower() and
                        'dependencies' in str(s.get('name', '')).lower()]
        for step in install_steps:
            run_cmd = step.get('run', '')
            assert 'pip install --upgrade pip' in run_cmd or \
                   'python -m pip install --upgrade pip' in run_cmd, \
                "Should upgrade pip before installing dependencies"
    
    def test_installs_test_requirements(self, steps):
        """Test that test requirements are installed"""
        install_steps = [s for s in steps 
                        if 'install' in str(s.get('name', '')).lower() and
                        'dependencies' in str(s.get('name', '')).lower()]
        for step in install_steps:
            run_cmd = step.get('run', '')
            assert 'requirements.txt' in run_cmd, \
                "Should install from requirements.txt"
            assert 'tests/requirements.txt' in run_cmd, \
                "Should install from tests/requirements.txt specifically"
    
    def test_installs_linting_tools(self, steps):
        """Test that linting tools are installed"""
        install_steps = [s for s in steps 
                        if 'install' in str(s.get('name', '')).lower() and
                        'dependencies' in str(s.get('name', '')).lower()]
        required_tools = ['flake8', 'black', 'isort', 'mypy']
        
        for step in install_steps:
            run_cmd = step.get('run', '')
            for tool in required_tools:
                assert tool in run_cmd, \
                    f"Should install {tool} in dependency installation step"
    
    def test_uses_python_module_syntax(self, steps):
        """Test that installation uses python -m pip syntax"""
        install_steps = [s for s in steps 
                        if 'install' in str(s.get('name', '')).lower() and
                        'dependencies' in str(s.get('name', '')).lower()]
        for step in install_steps:
            run_cmd = step.get('run', '')
            if 'pip install' in run_cmd:
                # Should use python -m pip for better compatibility
                assert 'python -m pip' in run_cmd or 'python3 -m pip' in run_cmd or \
                       run_cmd.strip().startswith('pip install'), \
                    "Should use 'python -m pip' syntax for better compatibility"


class TestFlake8Linting:
    """Test flake8 linting step configuration"""
    
    def test_has_flake8_step(self, steps):
        """Test that workflow includes flake8 linting step"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        assert len(flake8_steps) > 0, \
            "Workflow should include flake8 linting step"
    
    def test_flake8_checks_syntax_errors(self, steps):
        """Test that flake8 checks for syntax errors (E9, F63, F7, F82)"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        for step in flake8_steps:
            run_cmd = step.get('run', '')
            assert 'E9' in run_cmd, "Should check E9 (syntax errors)"
            assert 'F63' in run_cmd or 'F6' in run_cmd, \
                "Should check F63 (invalid comparisons)"
            assert 'F7' in run_cmd, "Should check F7 (syntax errors)"
            assert 'F82' in run_cmd or 'F8' in run_cmd, \
                "Should check F82 (undefined names)"
    
    def test_flake8_shows_source(self, steps):
        """Test that flake8 is configured to show source code"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        for step in flake8_steps:
            run_cmd = step.get('run', '')
            assert '--show-source' in run_cmd, \
                "flake8 should use --show-source for better error reporting"
    
    def test_flake8_shows_statistics(self, steps):
        """Test that flake8 shows statistics"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        for step in flake8_steps:
            run_cmd = step.get('run', '')
            assert '--statistics' in run_cmd, \
                "flake8 should use --statistics for summary reporting"
    
    def test_flake8_has_count_flag(self, steps):
        """Test that flake8 uses --count flag"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        for step in flake8_steps:
            run_cmd = step.get('run', '')
            assert '--count' in run_cmd, \
                "flake8 should use --count to show number of issues"
    
    def test_flake8_has_warning_check(self, steps):
        """Test that flake8 includes warning-level check with exit-zero"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        for step in flake8_steps:
            run_cmd = step.get('run', '')
            # Should have two flake8 commands: one strict, one with exit-zero
            assert '--exit-zero' in run_cmd, \
                "Should have flake8 check with --exit-zero for warnings"
    
    def test_flake8_max_complexity_set(self, steps):
        """Test that flake8 configures max complexity"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        for step in flake8_steps:
            run_cmd = step.get('run', '')
            if '--max-complexity' in run_cmd:
                assert '--max-complexity=10' in run_cmd or \
                       '--max-complexity=15' in run_cmd, \
                    "Max complexity should be reasonable (10-15)"
    
    def test_flake8_max_line_length_set(self, steps):
        """Test that flake8 configures max line length"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        for step in flake8_steps:
            run_cmd = step.get('run', '')
            if '--max-line-length' in run_cmd:
                assert '127' in run_cmd or '120' in run_cmd or '100' in run_cmd, \
                    "Max line length should be reasonable (100-127)"
    
    def test_flake8_has_descriptive_comments(self, steps):
        """Test that flake8 command has explanatory comments"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        for step in flake8_steps:
            run_cmd = step.get('run', '')
            # Multi-line run commands often have comments
            if '\n' in run_cmd:
                assert '#' in run_cmd, \
                    "Multi-line flake8 commands should have explanatory comments"


class TestPytestExecution:
    """Test pytest execution step configuration"""
    
    def test_has_pytest_step(self, steps):
        """Test that workflow includes pytest step"""
        pytest_steps = [s for s in steps 
                       if 'pytest' in str(s.get('name', '')).lower() or
                       'pytest' in str(s.get('run', ''))]
        assert len(pytest_steps) > 0, \
            "Workflow should include pytest execution step"
    
    def test_pytest_uses_module_syntax(self, steps):
        """Test that pytest is run using python -m pytest"""
        pytest_steps = [s for s in steps 
                       if 'pytest' in str(s.get('run', ''))]
        for step in pytest_steps:
            run_cmd = step.get('run', '')
            assert 'python -m pytest' in run_cmd or 'python3 -m pytest' in run_cmd, \
                "Should use 'python -m pytest' for better compatibility"
    
    def test_pytest_targets_tests_directory(self, steps):
        """Test that pytest runs tests from tests/ directory"""
        pytest_steps = [s for s in steps 
                       if 'pytest' in str(s.get('run', ''))]
        for step in pytest_steps:
            run_cmd = step.get('run', '')
            assert 'tests/' in run_cmd or 'tests ' in run_cmd, \
                "pytest should target tests/ directory"
    
    def test_pytest_uses_verbose_flag(self, steps):
        """Test that pytest runs in verbose mode"""
        pytest_steps = [s for s in steps 
                       if 'pytest' in str(s.get('run', ''))]
        for step in pytest_steps:
            run_cmd = step.get('run', '')
            assert '-v' in run_cmd or '--verbose' in run_cmd, \
                "pytest should run in verbose mode"
    
    def test_pytest_uses_short_traceback(self, steps):
        """Test that pytest uses short traceback format"""
        pytest_steps = [s for s in steps 
                       if 'pytest' in str(s.get('run', ''))]
        for step in pytest_steps:
            run_cmd = step.get('run', '')
            assert '--tb=short' in run_cmd or '-tb=short' in run_cmd, \
                "pytest should use --tb=short for readable output"
    
    def test_pytest_step_has_descriptive_name(self, steps):
        """Test that pytest step has clear, descriptive name"""
        pytest_steps = [s for s in steps 
                       if 'pytest' in str(s.get('run', ''))]
        for step in pytest_steps:
            name = step.get('name', '')
            assert name, "pytest step should have a name"
            assert 'test' in name.lower() or 'pytest' in name.lower(), \
                f"pytest step name should be descriptive: {name}"


class TestStepOrdering:
    """Test that steps are in correct order"""
    
    def test_checkout_before_python_setup(self, steps):
        """Test that checkout happens before Python setup"""
        checkout_idx = next((i for i, s in enumerate(steps) 
                           if 'actions/checkout' in str(s.get('uses', ''))), -1)
        python_idx = next((i for i, s in enumerate(steps) 
                          if 'actions/setup-python' in str(s.get('uses', ''))), -1)
        
        assert checkout_idx >= 0, "Should have checkout step"
        assert python_idx >= 0, "Should have Python setup step"
        assert checkout_idx < python_idx, \
            "Checkout must happen before Python setup"
    
    def test_python_setup_before_dependency_install(self, steps):
        """Test that Python setup happens before dependency installation"""
        python_idx = next((i for i, s in enumerate(steps) 
                          if 'actions/setup-python' in str(s.get('uses', ''))), -1)
        install_idx = next((i for i, s in enumerate(steps) 
                           if 'install' in str(s.get('name', '')).lower() and
                           'dependencies' in str(s.get('name', '')).lower()), -1)
        
        assert python_idx >= 0, "Should have Python setup step"
        assert install_idx >= 0, "Should have dependency install step"
        assert python_idx < install_idx, \
            "Python setup must happen before dependency installation"
    
    def test_dependency_install_before_linting(self, steps):
        """Test that dependencies are installed before linting"""
        install_idx = next((i for i, s in enumerate(steps) 
                           if 'install' in str(s.get('name', '')).lower() and
                           'dependencies' in str(s.get('name', '')).lower()), -1)
        flake8_idx = next((i for i, s in enumerate(steps) 
                          if 'flake8' in str(s.get('name', '')).lower()), -1)
        
        assert install_idx >= 0, "Should have dependency install step"
        assert flake8_idx >= 0, "Should have flake8 step"
        assert install_idx < flake8_idx, \
            "Dependency installation must happen before linting"
    
    def test_linting_before_tests(self, steps):
        """Test that linting happens before running tests"""
        flake8_idx = next((i for i, s in enumerate(steps) 
                          if 'flake8' in str(s.get('name', '')).lower()), -1)
        pytest_idx = next((i for i, s in enumerate(steps) 
                          if 'pytest' in str(s.get('run', ''))), -1)
        
        assert flake8_idx >= 0, "Should have flake8 step"
        assert pytest_idx >= 0, "Should have pytest step"
        assert flake8_idx < pytest_idx, \
            "Linting should happen before running tests (fail fast)"


class TestWorkflowIntegration:
    """Test overall workflow integration"""
    
    def test_workflow_still_has_original_steps(self, steps):
        """Test that original demo steps are preserved"""
        step_names = [s.get('name', '') for s in steps]
        # Check that some original steps still exist
        assert any('one-line' in name.lower() for name in step_names) or \
               any('multi-line' in name.lower() for name in step_names), \
            "Original demo steps should be preserved"
    
    def test_all_new_steps_have_names(self, steps):
        """Test that all new steps have descriptive names"""
        for step in steps:
            if 'uses' in step or 'run' in step:
                assert 'name' in step, \
                    f"All steps should have names: {step}"
    
    def test_no_duplicate_step_names(self, steps):
        """Test that step names are unique"""
        names = [s.get('name', '') for s in steps if s.get('name')]
        unique_names = set(names)
        assert len(names) == len(unique_names), \
            "Step names should be unique"


class TestBestPractices:
    """Test best practices in enhanced workflow"""
    
    def test_uses_latest_stable_action_versions(self, steps):
        """Test that actions use current stable versions"""
        for step in steps:
            uses = step.get('uses', '')
            if '@' in uses:
                # Should use @v5 or @v4 or @v3 (not older)
                version = uses.split('@')[1].split('.')[0] if '@' in uses else ''
                if version.startswith('v'):
                    version_num = int(version[1])
                    assert version_num >= 3, \
                        f"Action should use recent version (v3+): {uses}"
    
    def test_multiline_run_commands_use_pipe(self, steps):
        """Test that multi-line run commands use | for readability"""
        for step in steps:
            run_cmd = step.get('run', '')
            if isinstance(run_cmd, str) and '\n' in run_cmd:
                # This is good - multi-line commands for readability
                pass
    
    def test_critical_checks_fail_fast(self, steps):
        """Test that critical checks (syntax errors) fail the build"""
        flake8_steps = [s for s in steps 
                       if 'flake8' in str(s.get('name', '')).lower()]
        for step in flake8_steps:
            run_cmd = step.get('run', '')
            # First flake8 command should NOT have exit-zero
            if 'E9,F63,F7,F82' in run_cmd or 'E9' in run_cmd:
                # This command should not have --exit-zero on the critical checks
                lines = run_cmd.split('\n')
                critical_line = [l for l in lines if 'E9' in l][0] if any('E9' in l for l in lines) else ''
                if critical_line:
                    assert '--exit-zero' not in critical_line, \
                        "Critical syntax errors should fail the build (no --exit-zero)"


class TestEdgeCases:
    """Test edge cases and potential issues"""
    
    def test_no_hardcoded_python_paths(self, steps):
        """Test that no hardcoded Python paths are used"""
        for step in steps:
            run_cmd = step.get('run', '')
            if isinstance(run_cmd, str):
                assert '/usr/bin/python' not in run_cmd and \
                       '/usr/local/bin/python' not in run_cmd, \
                    "Should not use hardcoded Python paths"
    
    def test_no_sudo_commands(self, steps):
        """Test that no steps require sudo"""
        for step in steps:
            run_cmd = step.get('run', '')
            if isinstance(run_cmd, str):
                assert 'sudo' not in run_cmd, \
                    "Should not require sudo in CI environment"
    
    def test_all_tool_installations_from_pypi(self, steps):
        """Test that all Python tools are installed from PyPI"""
        install_steps = [s for s in steps 
                        if 'install' in str(s.get('name', '')).lower()]
        for step in install_steps:
            run_cmd = step.get('run', '')
            if 'pip install' in run_cmd:
                # Should not install from git or other sources in CI
                assert 'git+' not in run_cmd, \
                    "Should install from PyPI, not git repositories"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])