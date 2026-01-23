"""
Tests for .github/dependabot.yml configuration

This module contains comprehensive tests for the Dependabot configuration.
Tests cover:
- YAML structure and syntax validation
- Required fields and configuration options
- Schedule settings for automatic updates
- Security and best practices
- Package ecosystem configurations
- Commit message conventions
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope='module')
def dependabot_content(dependabot_path):
    """Load and parse dependabot.yml content"""
    with open(dependabot_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope='module')
def dependabot_raw(dependabot_path):
    """Get raw content of dependabot.yml"""
    with open(dependabot_path, 'r') as f:
        return f.read()


class TestDependabotStructure:
    """Test basic dependabot.yml structure"""
    
    def test_dependabot_file_exists(self, dependabot_path):
        """Test that dependabot.yml exists"""
        assert dependabot_path.exists(), "dependabot.yml should exist in .github/"
    
    def test_dependabot_is_valid_yaml(self, dependabot_content):
        """Test that dependabot.yml is valid YAML"""
        assert dependabot_content is not None, "Should parse as valid YAML"
    
    def test_has_version_field(self, dependabot_content):
        """Test that version field is present"""
        assert 'version' in dependabot_content, "Must have version field"
        assert dependabot_content['version'] == 2, "Should use Dependabot v2"
    
    def test_has_updates_section(self, dependabot_content):
        """Test that updates section exists"""
        assert 'updates' in dependabot_content, "Must have updates section"
        assert isinstance(dependabot_content['updates'], list), "Updates should be a list"


class TestPackageEcosystems:
    """Test package ecosystem configurations"""
    
    @pytest.fixture
    def ecosystems(self, dependabot_content):
        """Get list of configured ecosystems"""
        return [update['package-ecosystem'] for update in dependabot_content.get('updates', [])]
    
    def test_has_pip_ecosystem(self, ecosystems):
        """Test that pip ecosystem is configured"""
        assert 'pip' in ecosystems, "Should monitor Python pip dependencies"
    
    def test_has_github_actions_ecosystem(self, ecosystems):
        """Test that github-actions ecosystem is configured"""
        assert 'github-actions' in ecosystems, "Should monitor GitHub Actions versions"
    
    def test_has_docker_ecosystem(self, ecosystems):
        """Test that docker ecosystem is configured"""
        assert 'docker' in ecosystems, "Should monitor Docker images"
    
    def test_no_duplicate_ecosystems(self, ecosystems):
        """Test that there are no duplicate package ecosystems"""
        assert len(ecosystems) == len(set(ecosystems)), \
            "Should not have duplicate package ecosystems"


class TestPipConfiguration:
    """Test pip package ecosystem configuration"""
    
    @pytest.fixture
    def pip_config(self, dependabot_content):
        """Get pip update configuration"""
        for update in dependabot_content.get('updates', []):
            if update.get('package-ecosystem') == 'pip':
                return update
        return None
    
    def test_pip_config_exists(self, pip_config):
        """Test that pip configuration exists"""
        assert pip_config is not None, "Pip configuration should exist"
    
    def test_pip_directory_is_tests(self, pip_config):
        """Test that pip monitors tests directory"""
        assert pip_config['directory'] == '/tests', \
            "Should monitor /tests directory for pip dependencies"
    
    def test_pip_has_schedule(self, pip_config):
        """Test that pip updates have a schedule"""
        assert 'schedule' in pip_config, "Should have update schedule"
        schedule = pip_config['schedule']
        assert 'interval' in schedule, "Schedule should have interval"
    
    def test_pip_schedule_is_weekly(self, pip_config):
        """Test that pip updates run weekly"""
        schedule = pip_config['schedule']
        assert schedule['interval'] == 'weekly', "Should check weekly for updates"
    
    def test_pip_has_pr_limit(self, pip_config):
        """Test that pip has PR limit configured"""
        assert 'open-pull-requests-limit' in pip_config, "Should limit open PRs"
        limit = pip_config['open-pull-requests-limit']
        assert isinstance(limit, int) and limit > 0, "PR limit should be positive integer"
    
    def test_pip_has_reviewers(self, pip_config):
        """Test that pip updates have reviewers"""
        assert 'reviewers' in pip_config, "Should have reviewers configured"
        assert len(pip_config['reviewers']) > 0, "Should have at least one reviewer"


class TestScheduleConfiguration:
    """Test schedule configurations across all ecosystems"""
    
    def test_all_updates_have_schedules(self, dependabot_content):
        """Test that all update configurations have schedules"""
        for update in dependabot_content.get('updates', []):
            ecosystem = update.get('package-ecosystem')
            assert 'schedule' in update, f"{ecosystem} should have schedule"
    
    def test_schedules_have_day_specified(self, dependabot_content):
        """Test that weekly schedules specify a day"""
        for update in dependabot_content.get('updates', []):
            schedule = update.get('schedule', {})
            if schedule.get('interval') == 'weekly':
                assert 'day' in schedule, \
                    f"{update['package-ecosystem']} weekly schedule should specify day"
    
    def test_schedules_have_time_specified(self, dependabot_content):
        """Test that schedules specify a time"""
        for update in dependabot_content.get('updates', []):
            schedule = update.get('schedule', {})
            assert 'time' in schedule, \
                f"{update['package-ecosystem']} schedule should specify time"


class TestReviewersAndAssignees:
    """Test reviewer and assignee configurations"""
    
    def test_all_updates_have_reviewers(self, dependabot_content):
        """Test that all updates have reviewers configured"""
        for update in dependabot_content.get('updates', []):
            ecosystem = update.get('package-ecosystem')
            assert 'reviewers' in update, f"{ecosystem} should have reviewers"
            assert len(update['reviewers']) > 0, f"{ecosystem} should have at least one reviewer"
    
    def test_all_updates_have_assignees(self, dependabot_content):
        """Test that all updates have assignees configured"""
        for update in dependabot_content.get('updates', []):
            ecosystem = update.get('package-ecosystem')
            assert 'assignees' in update, f"{ecosystem} should have assignees"


class TestCommitMessageConfiguration:
    """Test commit message configurations"""
    
    def test_all_updates_have_commit_message_config(self, dependabot_content):
        """Test that all updates have commit message configuration"""
        for update in dependabot_content.get('updates', []):
            ecosystem = update.get('package-ecosystem')
            assert 'commit-message' in update, \
                f"{ecosystem} should have commit-message configuration"
    
    def test_commit_messages_have_prefix(self, dependabot_content):
        """Test that all commit message configs have a prefix"""
        for update in dependabot_content.get('updates', []):
            msg_config = update.get('commit-message', {})
            assert 'prefix' in msg_config, \
                f"{update['package-ecosystem']} commit-message should have prefix"


class TestYAMLFormatting:
    """Test YAML formatting and style"""
    
    def test_no_tabs_in_yaml(self, dependabot_raw):
        """Test that YAML uses spaces, not tabs"""
        assert '\t' not in dependabot_raw, "YAML should use spaces, not tabs"
    
    def test_consistent_indentation(self, dependabot_raw):
        """Test that indentation is consistent"""
        lines = dependabot_raw.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    assert leading_spaces % 2 == 0, \
                        f"Line {i} has inconsistent indentation (not multiple of 2)"
    
    def test_has_descriptive_comments(self, dependabot_raw):
        """Test that configuration has helpful comments"""
        assert '#' in dependabot_raw, "Should have comments explaining configuration"


class TestSecurityBestPractices:
    """Test security best practices in configuration"""
    
    def test_monitors_security_updates(self, dependabot_content):
        """Test that configuration enables security updates"""
        assert len(dependabot_content.get('updates', [])) > 0, \
            "Should have update configurations for security monitoring"
    
    def test_has_appropriate_update_frequency(self, dependabot_content):
        """Test that updates check frequently enough for security"""
        for update in dependabot_content.get('updates', []):
            schedule = update.get('schedule', {})
            interval = schedule.get('interval', '')
            assert interval in ['daily', 'weekly'], \
                f"{update['package-ecosystem']} should check at least weekly for security"


class TestEdgeCases:
    """Test edge cases and potential issues"""
    
    def test_file_is_not_empty(self, dependabot_raw):
        """Test that configuration file is not empty"""
        assert len(dependabot_raw.strip()) > 0, "File should not be empty"
    
    def test_updates_list_not_empty(self, dependabot_content):
        """Test that updates list has at least one entry"""
        updates = dependabot_content.get('updates', [])
        assert len(updates) > 0, "Should have at least one update configuration"
    
    def test_directories_use_absolute_paths(self, dependabot_content):
        """Test that directory paths start with /"""
        for update in dependabot_content.get('updates', []):
            directory = update.get('directory', '')
            assert directory.startswith('/'), \
                f"{update['package-ecosystem']} directory should be absolute path"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])