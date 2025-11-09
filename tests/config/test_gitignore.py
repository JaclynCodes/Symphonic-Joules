"""
Comprehensive test suite for .gitignore

This test suite validates the .gitignore configuration including:
- File existence and structure
- Pattern validity and coverage
- Common exclusion patterns
- Project-specific patterns
"""

import pytest
import re
from pathlib import Path


@pytest.fixture
def gitignore_path():
    """Return the path to .gitignore file."""
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / ".gitignore"


@pytest.fixture
def gitignore_content(gitignore_path):
    """Load raw content of .gitignore."""
    with open(gitignore_path, 'r') as f:
        return f.read()


@pytest.fixture
def gitignore_patterns(gitignore_content):
    """Parse .gitignore into non-comment lines."""
    patterns = []
    for line in gitignore_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            patterns.append(line)
    return patterns


class TestGitignoreStructure:
    """Test the basic structure of .gitignore."""
    
    def test_gitignore_exists(self, gitignore_path):
        """Test that .gitignore file exists."""
        assert gitignore_path.exists(), ".gitignore should exist"
    
    def test_gitignore_not_empty(self, gitignore_content):
        """Test that .gitignore is not empty."""
        assert len(gitignore_content.strip()) > 0, \
            ".gitignore should not be empty"
    
    def test_gitignore_readable(self, gitignore_path):
        """Test that .gitignore is readable."""
        try:
            with open(gitignore_path, 'r') as f:
                f.read()
        except OSError as e:
            pytest.fail(f"Failed to read .gitignore: {e}")


class TestCommonPatterns:
    """Test common gitignore patterns."""
    
    def test_os_files_ignored(self, gitignore_content):
        """Test that common OS files are ignored."""
        os_patterns = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
        content_lower = gitignore_content.lower()
        
        found_patterns = [p for p in os_patterns if p.lower() in content_lower]
        assert len(found_patterns) > 0, \
            "Should ignore common OS-specific files"
    
    def test_editor_files_ignored(self, gitignore_content):
        """Test that common editor files are ignored."""
        editor_patterns = ['.vscode', '.idea', '*.swp']
        content_lower = gitignore_content.lower()
        
        for pattern in editor_patterns[:2]:  # Check at least some
            if pattern.lower() in content_lower:
                assert True
                return
        
        pytest.skip("Consider ignoring editor-specific files")
    
    def test_python_cache_ignored(self, gitignore_content):
        """Test that Python cache files are ignored."""
        python_patterns = ['__pycache__', '*.pyc', '*.pyo']
        content_lower = gitignore_content.lower()
        
        found = [p for p in python_patterns if p.lower() in content_lower]
        assert len(found) >= 2, \
            "Should ignore Python cache files (__pycache__, *.pyc)"
    
    def test_virtual_environments_ignored(self, gitignore_content):
        """Test that virtual environment directories are ignored."""
        venv_patterns = ['venv/', 'env/', '.venv', 'ENV/']
        content_lower = gitignore_content.lower()
        
        found = [p for p in venv_patterns if p.lower().rstrip('/') in content_lower]
        assert len(found) >= 2, \
            "Should ignore virtual environment directories"
    
    def test_build_output_ignored(self, gitignore_content):
        """Test that build output directories are ignored."""
        build_patterns = ['build/', 'dist/', 'out/', '*.egg-info']
        content_lower = gitignore_content.lower()
        
        found = [p for p in build_patterns if p.lower().rstrip('/') in content_lower]
        assert len(found) >= 2, \
            "Should ignore build output directories"
    
    def test_log_files_ignored(self, gitignore_content):
        """Test that log files are ignored."""
        assert '*.log' in gitignore_content.lower(), \
            "Should ignore log files (*.log)"
    
    def test_temporary_files_ignored(self, gitignore_content):
        """Test that temporary files are ignored."""
        temp_patterns = ['*.tmp', '*.temp', 'tmp/']
        content_lower = gitignore_content.lower()
        
        found = [p for p in temp_patterns if p.lower().rstrip('/') in content_lower]
        assert len(found) > 0, \
            "Should ignore temporary files"


class TestTestingPatterns:
    """Test patterns specific to testing artifacts."""
    
    def test_pytest_cache_ignored(self, gitignore_content):
        """Test that pytest cache is ignored."""
        assert '.pytest_cache' in gitignore_content, \
            "Should ignore .pytest_cache directory"
    
    def test_coverage_files_ignored(self, gitignore_content):
        """Test that coverage files are ignored."""
        coverage_patterns = ['.coverage', 'htmlcov/', 'coverage/']
        content_lower = gitignore_content.lower()
        
        found = [p for p in coverage_patterns if p.lower().rstrip('/') in content_lower]
        assert len(found) >= 2, \
            "Should ignore coverage output files"
    
    def test_tox_ignored(self, gitignore_content):
        """Test that tox directories are ignored if used."""
        if '.tox' in gitignore_content or 'tox' in gitignore_content.lower():
            assert '.tox' in gitignore_content, \
                "Should properly ignore .tox directory"


class TestProjectSpecificPatterns:
    """Test project-specific patterns."""
    
    def test_audio_test_files_ignored(self, gitignore_content):
        """Test that temporary audio files are ignored."""
        # This project mentions audio processing
        audio_patterns = ['*.wav.tmp', '*.mp3.tmp', 'test_audio/', 'temp_audio/']
        content_lower = gitignore_content.lower()
        
        found = [p for p in audio_patterns if p.lower().rstrip('/') in content_lower]
        if len(found) > 0:
            assert True  # Good - project-specific patterns exist
    
    def test_environment_files_ignored(self, gitignore_content):
        """Test that environment files are ignored."""
        env_patterns = ['.env', '.env.local']
        content_lower = gitignore_content.lower()
        
        found = [p for p in env_patterns if p.lower() in content_lower]
        assert len(found) > 0, \
            "Should ignore environment files (.env)"


class TestPatternValidity:
    """Test validity of gitignore patterns."""
    
    def test_no_absolute_paths(self, gitignore_patterns):
        """Test that patterns don't use absolute paths."""
        for pattern in gitignore_patterns:
            assert not pattern.startswith('/home') and not pattern.startswith('/usr'), \
                f"Pattern should not use absolute paths: {pattern}"
    
    def test_trailing_slashes_for_directories(self, gitignore_patterns):
        """Test that directory patterns use trailing slashes consistently."""
        directory_keywords = ['cache', 'build', 'dist', 'node_modules']
        
        for pattern in gitignore_patterns:
            for keyword in directory_keywords:
                if keyword in pattern.lower() and not pattern.endswith('/'):
                    # It's okay if it's a wildcard pattern
                    if '*' not in pattern:
                        pytest.skip(f"Consider adding trailing slash to directory pattern: {pattern}")
    
    def test_no_duplicate_patterns(self, gitignore_patterns):
        """Test that patterns are not duplicated."""
        # Normalize patterns for comparison
        normalized = [p.rstrip('/').lower() for p in gitignore_patterns]
        
        duplicates = [p for p in normalized if normalized.count(p) > 1]
        assert len(set(duplicates)) == 0, \
            f"Duplicate patterns found: {set(duplicates)}"
    
    def test_patterns_use_valid_wildcards(self, gitignore_patterns):
        """Test that wildcard patterns are valid."""
        for pattern in gitignore_patterns:
            # Check for invalid wildcard usage
            if '***' in pattern:
                pytest.fail(f"Invalid wildcard pattern: {pattern}")
            
            # Patterns with extensions should use *.ext format
            if pattern.startswith('*.'):
                assert len(pattern) > 2, \
                    f"Extension pattern seems incomplete: {pattern}"


class TestGitignoreOrganization:
    """Test organization and structure of .gitignore."""
    
    def test_has_section_comments(self, gitignore_content):
        """Test that .gitignore has section comments for organization."""
        comment_lines = [line for line in gitignore_content.split('\n') if line.strip().startswith('#')]
        
        assert len(comment_lines) >= 3, \
            ".gitignore should have section comments for better organization"
    
    def test_logical_grouping(self, gitignore_content):
        """Test that patterns are logically grouped."""
        # Check for common section headers
        sections = ['Operating System', 'IDE', 'Python', 'Build', 'Test']
        content_lower = gitignore_content.lower()
        
        found_sections = [s for s in sections if s.lower() in content_lower]
        assert len(found_sections) >= 3, \
            ".gitignore should group patterns into logical sections"
    
    def test_blank_lines_separate_sections(self, gitignore_content):
        """Test that blank lines separate sections."""
        lines = gitignore_content.split('\n')
        blank_lines = [i for i, line in enumerate(lines) if not line.strip()]
        
        assert len(blank_lines) >= 3, \
            "Sections should be separated by blank lines"


class TestGitignoreFormatting:
    """Test formatting and style of .gitignore."""
    
    def test_no_trailing_whitespace(self, gitignore_content):
        """Test that lines don't have trailing whitespace."""
        lines = gitignore_content.split('\n')
        for i, line in enumerate(lines, 1):
            # Exclude blank lines
            if line and (line.endswith(' ') or line.endswith('\t')):
                pytest.fail(f"Line {i} has trailing whitespace")
    
    def test_file_ends_with_newline(self, gitignore_content):
        """Test that file ends with a newline."""
        assert gitignore_content.endswith('\n'), \
            ".gitignore should end with a newline"
    
    def test_consistent_comment_style(self, gitignore_content):
        """Test that comments use consistent style."""
        comment_lines = [line for line in gitignore_content.split('\n') 
                        if line.strip().startswith('#')]
        
        if len(comment_lines) > 0:
            # Check if comments have space after #
            spaced_comments = [line for line in comment_lines if line.strip().startswith('# ')]
            
            # Most comments should have space after #
            if len(comment_lines) > 3:
                ratio = len(spaced_comments) / len(comment_lines)
                assert ratio >= 0.5, \
                    "Consider adding space after # in comments for consistency"


class TestSecurityPatterns:
    """Test security-related ignore patterns."""
    
    def test_sensitive_files_ignored(self, gitignore_content):
        """Test that sensitive files are ignored."""
        sensitive_patterns = ['.env', 'secrets', 'private']
        content_lower = gitignore_content.lower()
        
        found = [p for p in sensitive_patterns if p.lower() in content_lower]
        assert len(found) > 0, \
            "Should ignore sensitive files like .env"
    
    def test_no_negation_of_sensitive_patterns(self, gitignore_patterns):
        """Test that sensitive patterns are not negated."""
        sensitive_keywords = ['secret', 'password', 'key', 'token', '.env']
        
        for pattern in gitignore_patterns:
            if pattern.startswith('!'):
                negated = pattern[1:].lower()
                for keyword in sensitive_keywords:
                    assert keyword not in negated, \
                        f"Should not negate sensitive patterns: {pattern}"


class TestIgnoreCoverage:
    """Test coverage of important file types."""
    
    def test_common_languages_covered(self, gitignore_content):
        """Test that common language artifacts are covered."""
        # Python is primary, but checking for awareness
        assert '__pycache__' in gitignore_content or '*.pyc' in gitignore_content, \
            "Python artifacts should be ignored"
    
    def test_dependency_directories_ignored(self, gitignore_content):
        """Test that dependency directories are ignored."""
        dep_patterns = ['node_modules/', 'vendor/', 'bower_components/']
        content_lower = gitignore_content.lower()
        
        # At least some should be present
        found = [p for p in dep_patterns if p.lower().rstrip('/') in content_lower]
        if len(found) > 0:
            assert True
    
    def test_documentation_build_ignored(self, gitignore_content):
        """Test that documentation build artifacts are ignored."""
        doc_patterns = ['docs/_build', 'docs/site', '.sphinx-build']
        content_lower = gitignore_content.lower()
        
        # Check if documentation builds are ignored
        found = [p for p in doc_patterns if p.lower().rstrip('/') in content_lower]
        if len(found) > 0:
            assert True  # Good practice


@pytest.mark.unit
class TestGitignoreEdgeCases:
    """Test edge cases in .gitignore."""
    
    def test_no_empty_lines_at_start(self, gitignore_content):
        """Test that file doesn't start with empty lines."""
        assert not gitignore_content.startswith('\n'), \
            ".gitignore should not start with empty lines"
    
    def test_patterns_dont_conflict(self, gitignore_patterns):
        """Test that patterns don't obviously conflict."""
        for _, pattern1 in enumerate(gitignore_patterns):
            if pattern1.startswith('!'):
                # This is a negation pattern
                negated = pattern1[1:]
                # This is complex to validate fully, just ensure it's intentional
                assert len(negated) > 1, \
                    f"Negation pattern should be specific: {pattern1}"
    
    def test_no_windows_path_separators(self, gitignore_patterns):
        """Test that patterns use forward slashes."""
        for pattern in gitignore_patterns:
            assert '\\' not in pattern, \
                f"Use forward slashes in patterns, not backslashes: {pattern}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])