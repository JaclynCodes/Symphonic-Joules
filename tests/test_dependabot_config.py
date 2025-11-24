"""
Tests for .github/dependabot.yml configuration

This module validates the Dependabot configuration for automated dependency updates:
- YAML structure and syntax
- Version specification
- Update schedules for different ecosystems
- Reviewer and assignee configuration
- Commit message prefixes
- Pull request limits
- Directory configurations
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def dependabot_path(repo_root):
    """Get path to dependabot configuration file"""
    return repo_root / '.github' / 'dependabot.yml'


@pytest.fixture(scope='module')
def dependabot_content(dependabot_path):
    """Load and parse dependabot configuration"""
    with open(dependabot_path, 'r') as f:
        return yaml.safe_load(f)


class TestDependabotStructure:
    """Test Dependabot configuration structure"""
    
    def test_dependabot_file_exists(self, dependabot_path):
        """Test that dependabot.yml exists at expected location"""
        assert dependabot_path.exists(), \
            f"Dependabot config not found at {dependabot_path}"
    
    def test_dependabot_is_valid_yaml(self, dependabot_content):
        """Test that dependabot.yml is valid YAML"""
        assert dependabot_content is not None, \
            "Dependabot configuration should not be None"
        assert isinstance(dependabot_content, dict), \
            "Dependabot configuration should be a dictionary"
    
    def test_has_version_field(self, dependabot_content):
        """Test that configuration specifies version"""
        assert 'version' in dependabot_content, \
            "Dependabot config must specify 'version'"
        assert dependabot_content['version'] == 2, \
            "Dependabot should use version 2"
    
    def test_has_updates_section(self, dependabot_content):
        """Test that configuration has updates section"""
        assert 'updates' in dependabot_content, \
            "Dependabot config must have 'updates' section"
        assert isinstance(dependabot_content['updates'], list), \
            "'updates' should be a list"
        assert len(dependabot_content['updates']) > 0, \
            "'updates' section should not be empty"


class TestPackageEcosystems:
    """Test package ecosystem configurations"""
    
    def test_has_pip_ecosystem(self, dependabot_content):
        """Test that pip ecosystem is configured"""
        ecosystems = [update.get('package-ecosystem') 
                     for update in dependabot_content['updates']]
        assert 'pip' in ecosystems, \
            "Should configure pip ecosystem for Python dependencies"
    
    def test_has_github_actions_ecosystem(self, dependabot_content):
        """Test that github-actions ecosystem is configured"""
        ecosystems = [update.get('package-ecosystem') 
                     for update in dependabot_content['updates']]
        assert 'github-actions' in ecosystems, \
            "Should configure github-actions ecosystem"
    
    def test_has_docker_ecosystem(self, dependabot_content):
        """Test that docker ecosystem is configured"""
        ecosystems = [update.get('package-ecosystem') 
                     for update in dependabot_content['updates']]
        assert 'docker' in ecosystems, \
            "Should configure docker ecosystem for future support"
    
    def test_all_ecosystems_have_required_fields(self, dependabot_content):
        """Test that each ecosystem has all required fields"""
        required_fields = ['package-ecosystem', 'directory', 'schedule']
        
        for update in dependabot_content['updates']:
            for field in required_fields:
                assert field in update, \
                    f"Update for {update.get('package-ecosystem')} " \
                    f"missing required field '{field}'"


class TestPipConfiguration:
    """Test pip (Python) ecosystem configuration"""
    
    @pytest.fixture
    def pip_config(self, dependabot_content):
        """Get pip ecosystem configuration"""
        for update in dependabot_content['updates']:
            if update.get('package-ecosystem') == 'pip':
                return update
        pytest.fail("No pip configuration found")
    
    def test_pip_directory_points_to_tests(self, pip_config):
        """Test that pip checks tests directory"""
        assert pip_config['directory'] == '/tests', \
            "pip should check /tests directory"
    
    def test_pip_has_weekly_schedule(self, pip_config):
        """Test that pip updates are scheduled weekly"""
        assert pip_config['schedule']['interval'] == 'weekly', \
            "pip updates should run weekly"
    
    def test_pip_schedule_on_monday(self, pip_config):
        """Test that pip updates run on Monday"""
        assert pip_config['schedule']['day'] == 'monday', \
            "pip updates should run on Monday"
    
    def test_pip_has_pr_limit(self, pip_config):
        """Test that pip has pull request limit"""
        assert 'open-pull-requests-limit' in pip_config, \
            "pip should have PR limit"
        assert pip_config['open-pull-requests-limit'] == 10, \
            "pip should allow up to 10 open PRs"
    
    def test_pip_has_reviewers(self, pip_config):
        """Test that pip PRs have reviewers configured"""
        assert 'reviewers' in pip_config, \
            "pip should have reviewers configured"
        assert 'JaclynCodes' in pip_config['reviewers'], \
            "JaclynCodes should be a reviewer"
    
    def test_pip_commit_message_prefix(self, pip_config):
        """Test that pip has commit message prefix"""
        assert 'commit-message' in pip_config, \
            "pip should have commit-message configuration"
        assert pip_config['commit-message']['prefix'] == 'deps', \
            "pip commits should use 'deps' prefix"


class TestGitHubActionsConfiguration:
    """Test GitHub Actions ecosystem configuration"""
    
    @pytest.fixture
    def actions_config(self, dependabot_content):
        """Get GitHub Actions ecosystem configuration"""
        for update in dependabot_content['updates']:
            if update.get('package-ecosystem') == 'github-actions':
                return update
        pytest.fail("No github-actions configuration found")
    
    def test_actions_directory_is_root(self, actions_config):
        """Test that actions checks root directory"""
        assert actions_config['directory'] == '/', \
            "github-actions should check root directory"
    
    def test_actions_has_weekly_schedule(self, actions_config):
        """Test that actions updates are scheduled weekly"""
        assert actions_config['schedule']['interval'] == 'weekly', \
            "github-actions updates should run weekly"
    
    def test_actions_commit_message_prefix(self, actions_config):
        """Test that actions use ci prefix"""
        assert actions_config['commit-message']['prefix'] == 'ci', \
            "github-actions commits should use 'ci' prefix"


class TestSecurityBestPractices:
    """Test security and best practices"""
    
    def test_all_ecosystems_have_reviewers(self, dependabot_content):
        """Test that all ecosystems require code review"""
        for update in dependabot_content['updates']:
            assert 'reviewers' in update, \
                f"{update['package-ecosystem']} should have reviewers"
            assert len(update['reviewers']) > 0, \
                f"{update['package-ecosystem']} needs reviewers"
    
    def test_pr_limits_are_reasonable(self, dependabot_content):
        """Test that PR limits prevent flooding"""
        for update in dependabot_content['updates']:
            limit = update.get('open-pull-requests-limit', 0)
            assert limit > 0 and limit <= 10, \
                f"{update['package-ecosystem']} PR limit should be 1-10"
    
    def test_commit_messages_have_prefixes(self, dependabot_content):
        """Test that commit messages use conventional commits"""
        for update in dependabot_content['updates']:
            if 'commit-message' in update:
                assert 'prefix' in update['commit-message'], \
                    f"{update['package-ecosystem']} should have commit prefix"


class TestEdgeCases:
    """Test edge cases and configuration validity"""
    
    def test_no_duplicate_ecosystems(self, dependabot_content):
        """Test that each ecosystem is configured only once"""
        ecosystems = [update['package-ecosystem'] 
                     for update in dependabot_content['updates']]
        assert len(ecosystems) == len(set(ecosystems)), \
            "Each ecosystem should be configured only once"
    
    def test_file_has_comments(self, dependabot_path):
        """Test that configuration file has helpful comments"""
        with open(dependabot_path, 'r') as f:
            content = f.read()
            assert '#' in content, \
                "Configuration should have comments"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])