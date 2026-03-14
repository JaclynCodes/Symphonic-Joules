"""
Comprehensive tests for .github/dependabot.yml configuration.

This module validates the Dependabot configuration for automated dependency updates:
- YAML structure and syntax
- Version specification
- Package ecosystem configurations
- Schedule settings
- PR limits and reviewer assignments
- Commit message prefixes
- Directory paths
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope='module')
def dependabot_raw(dependabot_path):
    """Load raw dependabot configuration content"""
    with open(dependabot_path, 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def dependabot_config(dependabot_raw):
    """Parse dependabot configuration"""
    return yaml.safe_load(dependabot_raw)


@pytest.fixture(scope='module')
def updates_list(dependabot_config):
    """Get list of update configurations"""
    return dependabot_config.get('updates', [])


class TestDependabotFileStructure:
    """Test dependabot.yml file structure and accessibility"""
    
    def test_dependabot_file_exists(self, dependabot_path):
        """Test that dependabot.yml exists in correct location"""
        assert dependabot_path.exists(), \
            "dependabot.yml should exist at .github/dependabot.yml"
    
    def test_dependabot_file_is_readable(self, dependabot_path):
        """Test that dependabot.yml is readable"""
        with open(dependabot_path, 'r') as f:
            content = f.read()
            assert len(content) > 0, "dependabot.yml should not be empty"
    
    def test_dependabot_is_valid_yaml(self, dependabot_raw):
        """Test that dependabot.yml contains valid YAML"""
        try:
            yaml.safe_load(dependabot_raw)
        except yaml.YAMLError as e:
            pytest.fail(f"dependabot.yml contains invalid YAML: {e}")
    
    def test_dependabot_has_no_tabs(self, dependabot_raw):
        """Test that dependabot.yml uses spaces, not tabs"""
        assert '\t' not in dependabot_raw, \
            "dependabot.yml should use spaces for indentation, not tabs"
    
    def test_dependabot_has_comment_header(self, dependabot_raw):
        """Test that dependabot.yml has a descriptive comment header"""
        lines = dependabot_raw.split('\n')
        assert any('Dependabot' in line or 'dependency' in line.lower() 
                   for line in lines[:5]), \
            "File should have descriptive comment header"


class TestDependabotVersion:
    """Test Dependabot version specification"""
    
    def test_has_version_field(self, dependabot_config):
        """Test that configuration specifies version"""
        assert 'version' in dependabot_config, \
            "Configuration must specify 'version' field"
    
    def test_version_is_2(self, dependabot_config):
        """Test that configuration uses version 2"""
        assert dependabot_config['version'] == 2, \
            "Should use Dependabot version 2 (current stable)"
    
    def test_version_is_integer(self, dependabot_config):
        """Test that version is specified as integer"""
        assert isinstance(dependabot_config['version'], int), \
            "Version should be specified as integer, not string"


class TestUpdatesConfiguration:
    """Test updates configuration structure"""
    
    def test_has_updates_field(self, dependabot_config):
        """Test that configuration has updates field"""
        assert 'updates' in dependabot_config, \
            "Configuration must have 'updates' field"
    
    def test_updates_is_list(self, updates_list):
        """Test that updates is a list"""
        assert isinstance(updates_list, list), \
            "'updates' should be a list of configurations"
    
    def test_updates_not_empty(self, updates_list):
        """Test that updates list is not empty"""
        assert len(updates_list) > 0, \
            "Should have at least one update configuration"
    
    def test_all_updates_are_dicts(self, updates_list):
        """Test that all update entries are dictionaries"""
        for i, update in enumerate(updates_list):
            assert isinstance(update, dict), \
                f"Update entry {i} should be a dictionary"


class TestPackageEcosystems:
    """Test package ecosystem configurations"""
    
    def test_has_pip_ecosystem(self, updates_list):
        """Test that pip ecosystem is configured"""
        ecosystems = [u.get('package-ecosystem') for u in updates_list]
        assert 'pip' in ecosystems, \
            "Should configure pip for Python dependencies"
    
    def test_has_github_actions_ecosystem(self, updates_list):
        """Test that github-actions ecosystem is configured"""
        ecosystems = [u.get('package-ecosystem') for u in updates_list]
        assert 'github-actions' in ecosystems, \
            "Should configure github-actions for workflow dependencies"
    
    def test_has_docker_ecosystem(self, updates_list):
        """Test that docker ecosystem is configured"""
        ecosystems = [u.get('package-ecosystem') for u in updates_list]
        assert 'docker' in ecosystems, \
            "Should configure docker for future Dockerfile support"
    
    def test_all_ecosystems_valid(self, updates_list):
        """Test that all ecosystems use valid values"""
        valid_ecosystems = [
            'bundler', 'cargo', 'composer', 'docker', 'elm', 'gitsubmodule',
            'github-actions', 'gomod', 'gradle', 'maven', 'mix', 'npm',
            'nuget', 'pip', 'terraform'
        ]
        for update in updates_list:
            ecosystem = update.get('package-ecosystem')
            assert ecosystem in valid_ecosystems, \
                f"'{ecosystem}' is not a valid package ecosystem"


class TestDirectoryConfiguration:
    """Test directory path configurations"""
    
    def test_pip_directory_is_tests(self, updates_list):
        """Test that pip ecosystem monitors /tests directory"""
        pip_config = next((u for u in updates_list 
                          if u.get('package-ecosystem') == 'pip'), None)
        assert pip_config is not None, "Should have pip configuration"
        assert pip_config.get('directory') == '/tests', \
            "pip should monitor /tests directory for requirements.txt"
    
    def test_github_actions_directory_is_root(self, updates_list):
        """Test that github-actions monitors root directory"""
        actions_config = next((u for u in updates_list 
                              if u.get('package-ecosystem') == 'github-actions'), None)
        assert actions_config is not None, "Should have github-actions configuration"
        assert actions_config.get('directory') == '/', \
            "github-actions should monitor root directory for workflows"
    
    def test_docker_directory_is_root(self, updates_list):
        """Test that docker monitors root directory"""
        docker_config = next((u for u in updates_list 
                             if u.get('package-ecosystem') == 'docker'), None)
        assert docker_config is not None, "Should have docker configuration"
        assert docker_config.get('directory') == '/', \
            "docker should monitor root directory"
    
    def test_all_directories_start_with_slash(self, updates_list):
        """Test that all directories use absolute paths"""
        for update in updates_list:
            directory = update.get('directory')
            assert directory is not None, "All updates should specify directory"
            assert directory.startswith('/'), \
                f"Directory '{directory}' should start with '/'"


class TestScheduleConfiguration:
    """Test update schedule configurations"""
    
    def test_all_have_schedule(self, updates_list):
        """Test that all ecosystems have schedule configured"""
        for update in updates_list:
            ecosystem = update.get('package-ecosystem')
            assert 'schedule' in update, \
                f"{ecosystem} should have schedule configuration"
    
    def test_all_schedules_are_weekly(self, updates_list):
        """Test that all schedules use weekly interval"""
        for update in updates_list:
            schedule = update.get('schedule', {})
            interval = schedule.get('interval')
            assert interval == 'weekly', \
                f"All schedules should use 'weekly' interval, got '{interval}'"
    
    def test_all_schedules_on_monday(self, updates_list):
        """Test that all schedules run on Monday"""
        for update in updates_list:
            schedule = update.get('schedule', {})
            day = schedule.get('day')
            assert day == 'monday', \
                f"All schedules should run on 'monday', got '{day}'"
    
    def test_all_schedules_at_9am(self, updates_list):
        """Test that all schedules run at 09:00"""
        for update in updates_list:
            schedule = update.get('schedule', {})
            time = schedule.get('time')
            assert time == '09:00', \
                f"All schedules should run at '09:00', got '{time}'"
    
    def test_schedule_time_format(self, updates_list):
        """Test that time uses HH:MM format"""
        import re
        time_pattern = re.compile(r'^\d{2}:\d{2}$')
        for update in updates_list:
            schedule = update.get('schedule', {})
            time = schedule.get('time', '')
            assert time_pattern.match(time), \
                f"Time should be in HH:MM format, got '{time}'"


class TestPullRequestLimits:
    """Test pull request limit configurations"""
    
    def test_pip_has_pr_limit(self, updates_list):
        """Test that pip configuration has PR limit"""
        pip_config = next((u for u in updates_list 
                          if u.get('package-ecosystem') == 'pip'), None)
        assert 'open-pull-requests-limit' in pip_config, \
            "pip should have open-pull-requests-limit configured"
    
    def test_pip_pr_limit_is_10(self, updates_list):
        """Test that pip allows up to 10 open PRs"""
        pip_config = next((u for u in updates_list 
                          if u.get('package-ecosystem') == 'pip'), None)
        assert pip_config.get('open-pull-requests-limit') == 10, \
            "pip should allow 10 concurrent PRs for test dependencies"
    
    def test_github_actions_pr_limit_is_5(self, updates_list):
        """Test that github-actions allows up to 5 open PRs"""
        actions_config = next((u for u in updates_list 
                              if u.get('package-ecosystem') == 'github-actions'), None)
        assert actions_config.get('open-pull-requests-limit') == 5, \
            "github-actions should allow 5 concurrent PRs"
    
    def test_docker_pr_limit_is_5(self, updates_list):
        """Test that docker allows up to 5 open PRs"""
        docker_config = next((u for u in updates_list 
                             if u.get('package-ecosystem') == 'docker'), None)
        assert docker_config.get('open-pull-requests-limit') == 5, \
            "docker should allow 5 concurrent PRs"
    
    def test_all_pr_limits_are_positive_integers(self, updates_list):
        """Test that all PR limits are positive integers"""
        for update in updates_list:
            limit = update.get('open-pull-requests-limit')
            assert isinstance(limit, int), \
                f"PR limit should be integer, got {type(limit)}"
            assert limit > 0, \
                f"PR limit should be positive, got {limit}"


class TestReviewersAndAssignees:
    """Test reviewer and assignee configurations"""
    
    def test_all_have_reviewers(self, updates_list):
        """Test that all ecosystems assign reviewers"""
        for update in updates_list:
            ecosystem = update.get('package-ecosystem')
            assert 'reviewers' in update, \
                f"{ecosystem} should have reviewers configured"
    
    def test_all_have_assignees(self, updates_list):
        """Test that all ecosystems assign PRs to someone"""
        for update in updates_list:
            ecosystem = update.get('package-ecosystem')
            assert 'assignees' in update, \
                f"{ecosystem} should have assignees configured"
    
    def test_reviewers_include_jaclyncodes(self, updates_list):
        """Test that JaclynCodes is configured as reviewer"""
        for update in updates_list:
            reviewers = update.get('reviewers', [])
            assert 'JaclynCodes' in reviewers, \
                "JaclynCodes should be a reviewer for all PRs"
    
    def test_assignees_include_jaclyncodes(self, updates_list):
        """Test that JaclynCodes is configured as assignee"""
        for update in updates_list:
            assignees = update.get('assignees', [])
            assert 'JaclynCodes' in assignees, \
                "JaclynCodes should be assigned to all PRs"
    
    def test_reviewers_are_lists(self, updates_list):
        """Test that reviewers are specified as lists"""
        for update in updates_list:
            reviewers = update.get('reviewers')
            assert isinstance(reviewers, list), \
                "reviewers should be a list"
    
    def test_assignees_are_lists(self, updates_list):
        """Test that assignees are specified as lists"""
        for update in updates_list:
            assignees = update.get('assignees')
            assert isinstance(assignees, list), \
                "assignees should be a list"


class TestCommitMessageConfiguration:
    """Test commit message configurations"""
    
    def test_all_have_commit_message_config(self, updates_list):
        """Test that all ecosystems configure commit messages"""
        for update in updates_list:
            ecosystem = update.get('package-ecosystem')
            assert 'commit-message' in update, \
                f"{ecosystem} should have commit-message configuration"
    
    def test_pip_uses_deps_prefix(self, updates_list):
        """Test that pip uses 'deps' prefix"""
        pip_config = next((u for u in updates_list 
                          if u.get('package-ecosystem') == 'pip'), None)
        commit_msg = pip_config.get('commit-message', {})
        assert commit_msg.get('prefix') == 'deps', \
            "pip should use 'deps' commit message prefix"
    
    def test_github_actions_uses_ci_prefix(self, updates_list):
        """Test that github-actions uses 'ci' prefix"""
        actions_config = next((u for u in updates_list 
                              if u.get('package-ecosystem') == 'github-actions'), None)
        commit_msg = actions_config.get('commit-message', {})
        assert commit_msg.get('prefix') == 'ci', \
            "github-actions should use 'ci' commit message prefix"
    
    def test_docker_uses_docker_prefix(self, updates_list):
        """Test that docker uses 'docker' prefix"""
        docker_config = next((u for u in updates_list 
                             if u.get('package-ecosystem') == 'docker'), None)
        commit_msg = docker_config.get('commit-message', {})
        assert commit_msg.get('prefix') == 'docker', \
            "docker should use 'docker' commit message prefix"
    
    def test_all_include_scope(self, updates_list):
        """Test that all commit messages include scope"""
        for update in updates_list:
            commit_msg = update.get('commit-message', {})
            assert commit_msg.get('include') == 'scope', \
                "All commit messages should include scope"
    
    def test_pip_has_development_prefix(self, updates_list):
        """Test that pip configures development dependency prefix"""
        pip_config = next((u for u in updates_list 
                          if u.get('package-ecosystem') == 'pip'), None)
        commit_msg = pip_config.get('commit-message', {})
        assert 'prefix-development' in commit_msg, \
            "pip should configure prefix for development dependencies"
        assert commit_msg.get('prefix-development') == 'deps-dev', \
            "pip should use 'deps-dev' for development dependencies"


class TestConfigurationConsistency:
    """Test consistency across all ecosystem configurations"""
    
    def test_all_configs_have_required_fields(self, updates_list):
        """Test that all configurations have required fields"""
        required_fields = [
            'package-ecosystem', 'directory', 'schedule',
            'open-pull-requests-limit', 'reviewers', 'assignees', 'commit-message'
        ]
        for update in updates_list:
            ecosystem = update.get('package-ecosystem')
            for field in required_fields:
                assert field in update, \
                    f"{ecosystem} configuration missing required field '{field}'"
    
    def test_schedule_consistency(self, updates_list):
        """Test that all schedules are configured identically"""
        schedules = [u.get('schedule') for u in updates_list]
        first_schedule = schedules[0]
        for schedule in schedules[1:]:
            assert schedule == first_schedule, \
                "All ecosystems should have identical schedule configuration"
    
    def test_reviewer_consistency(self, updates_list):
        """Test that all configs have same reviewers"""
        reviewers_sets = [set(u.get('reviewers', [])) for u in updates_list]
        first_reviewers = reviewers_sets[0]
        for reviewers in reviewers_sets[1:]:
            assert reviewers == first_reviewers, \
                "All ecosystems should have identical reviewers"
    
    def test_assignee_consistency(self, updates_list):
        """Test that all configs have same assignees"""
        assignees_sets = [set(u.get('assignees', [])) for u in updates_list]
        first_assignees = assignees_sets[0]
        for assignees in assignees_sets[1:]:
            assert assignees == first_assignees, \
                "All ecosystems should have identical assignees"


class TestSecurityBestPractices:
    """Test security and best practice configurations"""
    
    def test_no_hardcoded_tokens(self, dependabot_raw):
        """Test that no API tokens are hardcoded"""
        sensitive_patterns = ['token', 'password', 'secret', 'key']
        lines = dependabot_raw.lower().split('\n')
        for line in lines:
            if ':' in line and not line.strip().startswith('#'):
                for pattern in sensitive_patterns:
                    if pattern in line:
                        # Make sure it's in a comment or is the word 'key' in another context
                        assert line.strip().startswith('#') or 'package-ecosystem' in line, \
                            f"Potential sensitive data in config: {line[:50]}"
    
    def test_reasonable_pr_limits(self, updates_list):
        """Test that PR limits are reasonable (not too high)"""
        for update in updates_list:
            limit = update.get('open-pull-requests-limit', 0)
            assert limit <= 20, \
                f"PR limit {limit} may be too high and spam maintainers"
    
    def test_schedule_not_too_frequent(self, updates_list):
        """Test that update schedule is not overly aggressive"""
        for update in updates_list:
            schedule = update.get('schedule', {})
            interval = schedule.get('interval', '')
            assert interval in ['weekly', 'monthly'], \
                f"Schedule '{interval}' may be too frequent; use weekly or monthly"


class TestDocumentationQuality:
    """Test documentation and comments in configuration"""
    
    def test_has_introductory_comment(self, dependabot_raw):
        """Test that file starts with descriptive comment"""
        lines = dependabot_raw.split('\n')
        first_non_empty = next((line for line in lines if line.strip()), '')
        assert first_non_empty.startswith('#'), \
            "File should start with descriptive comment"
    
    def test_ecosystems_have_comments(self, dependabot_raw):
        """Test that each ecosystem section has explanatory comments"""
        lines = dependabot_raw.split('\n')
        ecosystem_count = dependabot_raw.count('package-ecosystem:')
        comment_count = sum(1 for line in lines 
                           if line.strip().startswith('#') and 
                           ('version' in line.lower() or 'enable' in line.lower() or
                            'pip' in line.lower() or 'actions' in line.lower() or
                            'docker' in line.lower()))
        assert comment_count >= ecosystem_count, \
            "Each ecosystem configuration should have explanatory comments"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_no_duplicate_ecosystems(self, updates_list):
        """Test that no ecosystem is configured multiple times"""
        ecosystems = [u.get('package-ecosystem') for u in updates_list]
        assert len(ecosystems) == len(set(ecosystems)), \
            "Each ecosystem should only be configured once"
    
    def test_no_empty_reviewer_lists(self, updates_list):
        """Test that reviewer lists are not empty"""
        for update in updates_list:
            reviewers = update.get('reviewers', [])
            assert len(reviewers) > 0, \
                "Reviewer list should not be empty"
    
    def test_no_empty_assignee_lists(self, updates_list):
        """Test that assignee lists are not empty"""
        for update in updates_list:
            assignees = update.get('assignees', [])
            assert len(assignees) > 0, \
                "Assignee list should not be empty"
    
    def test_directory_paths_valid(self, updates_list):
        """Test that directory paths are valid"""
        for update in updates_list:
            directory = update.get('directory', '')
            assert not directory.endswith('/') or directory == '/', \
                "Directory path should not end with '/' unless it is root"
            assert '..' not in directory, \
                "Directory path should not contain '..'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])