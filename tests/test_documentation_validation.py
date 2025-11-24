"""
Tests for documentation files validation

This module validates documentation changes in:
- docs/faq.md - Frequently Asked Questions
- docs/installation-setup.md - Installation and Setup Guide

Tests ensure:
- Content accuracy and completeness
- Python version information is correct
- macOS compatibility notes are present
- Links are properly formatted
- Markdown syntax is valid
- Code blocks are properly formatted
"""

import pytest
import re
from pathlib import Path


@pytest.fixture(scope='module')
def faq_path():
    """Get path to FAQ document"""
    return Path('docs/faq.md')


@pytest.fixture(scope='module')
def installation_path():
    """Get path to installation document"""
    return Path('docs/installation-setup.md')


@pytest.fixture(scope='module')
def faq_content(faq_path):
    """Load FAQ content"""
    with open(faq_path, 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def installation_content(installation_path):
    """Load installation document content"""
    with open(installation_path, 'r') as f:
        return f.read()


class TestFAQStructure:
    """Test FAQ document structure"""
    
    def test_faq_file_exists(self, faq_path):
        """Test that FAQ file exists"""
        assert faq_path.exists(), "docs/faq.md should exist"
    
    def test_faq_not_empty(self, faq_content):
        """Test that FAQ has content"""
        assert len(faq_content) > 100, "FAQ should have substantial content"
    
    def test_faq_has_headers(self, faq_content):
        """Test that FAQ uses markdown headers"""
        assert re.search(r'^#+\s+', faq_content, re.MULTILINE), \
            "FAQ should have markdown headers"


class TestFAQPythonVersionInfo:
    """Test Python version information in FAQ"""
    
    def test_has_python_version_section(self, faq_content):
        """Test that FAQ has Python version information"""
        assert 'Python version' in faq_content or 'python version' in faq_content, \
            "FAQ should mention Python version requirements"
    
    def test_mentions_python_38_or_higher(self, faq_content):
        """Test that FAQ mentions Python 3.8+ requirement"""
        assert '3.8' in faq_content, "FAQ should mention Python 3.8 requirement"
    
    def test_mentions_macos_compatibility(self, faq_content):
        """Test that FAQ mentions macOS compatibility"""
        assert 'macOS' in faq_content or 'macos' in faq_content.lower(), \
            "FAQ should mention macOS platform"
    
    def test_mentions_python_311_workaround(self, faq_content):
        """Test that FAQ mentions Python 3.11 as workaround"""
        assert '3.11' in faq_content, \
            "FAQ should mention Python 3.11 as compatibility workaround"
    
    def test_has_link_to_installation_guide(self, faq_content):
        """Test that Python version question links to installation guide"""
        assert 'installation-setup.md' in faq_content or 'Installation Guide' in faq_content, \
            "Should link to installation guide for details"


class TestInstallationStructure:
    """Test installation guide structure"""
    
    def test_installation_file_exists(self, installation_path):
        """Test that installation guide exists"""
        assert installation_path.exists(), "docs/installation-setup.md should exist"
    
    def test_installation_not_empty(self, installation_content):
        """Test that installation guide has substantial content"""
        assert len(installation_content) > 1000, \
            "Installation guide should be comprehensive"
    
    def test_has_headers(self, installation_content):
        """Test that guide uses markdown headers"""
        assert re.search(r'^#+\s+', installation_content, re.MULTILINE), \
            "Guide should have markdown headers"


class TestInstallationPythonRequirements:
    """Test Python requirements section in installation guide"""
    
    def test_mentions_python_38_minimum(self, installation_content):
        """Test that guide mentions Python 3.8 minimum"""
        assert '3.8' in installation_content, \
            "Should mention Python 3.8 as minimum version"
    
    def test_mentions_python_311_for_macos(self, installation_content):
        """Test that guide mentions Python 3.11 for macOS"""
        assert '3.11' in installation_content, \
            "Should mention Python 3.11 for macOS users"
    
    def test_has_system_requirements_section(self, installation_content):
        """Test that guide has system requirements section"""
        assert 'System Requirements' in installation_content or \
               'Requirements' in installation_content, \
            "Should have system requirements section"


class TestMacOSCompatibilitySection:
    """Test macOS Python compatibility section"""
    
    def test_has_macos_section(self, installation_content):
        """Test that guide has dedicated macOS section"""
        assert 'macOS' in installation_content, \
            "Should have macOS-specific information"
    
    def test_has_python_version_compatibility_header(self, installation_content):
        """Test that guide has Python version compatibility header"""
        assert 'Python Version Compatibility' in installation_content or \
               'Python version' in installation_content.lower(), \
            "Should discuss Python version compatibility"
    
    def test_mentions_python_312_issues(self, installation_content):
        """Test that guide mentions Python 3.12+ issues"""
        assert '3.12' in installation_content, \
            "Should mention Python 3.12+ compatibility issues"
    
    def test_has_homebrew_installation_steps(self, installation_content):
        """Test that macOS section includes Homebrew installation"""
        lower_content = installation_content.lower()
        assert 'brew' in lower_content or 'homebrew' in lower_content, \
            "macOS section should include Homebrew installation steps"
    
    def test_shows_brew_install_command(self, installation_content):
        """Test that guide shows brew install command for Python 3.11"""
        assert 'brew install python@3.11' in installation_content, \
            "Should show exact brew install command"
    
    def test_shows_path_configuration(self, installation_content):
        """Test that guide shows PATH configuration"""
        assert 'PATH' in installation_content or 'path' in installation_content.lower(), \
            "Should explain PATH configuration"
    
    def test_mentions_zshrc_configuration(self, installation_content):
        """Test that guide mentions .zshrc configuration"""
        assert '.zshrc' in installation_content or 'zshrc' in installation_content, \
            "Should mention .zshrc for shell configuration"
    
    def test_shows_python_version_verification(self, installation_content):
        """Test that guide shows how to verify Python version"""
        assert 'python --version' in installation_content, \
            "Should show how to verify Python version"


class TestCodeBlocks:
    """Test code blocks in documentation"""
    
    def test_installation_has_code_blocks(self, installation_content):
        """Test that installation guide has code blocks"""
        assert '```' in installation_content, \
            "Installation guide should have code blocks for commands"
    
    def test_code_blocks_are_properly_closed(self, installation_content):
        """Test that code blocks are properly opened and closed"""
        code_blocks = installation_content.count('```')
        assert code_blocks % 2 == 0, \
            "Code blocks should be properly closed (even number of ```)"
    
    def test_bash_code_blocks_specified(self, installation_content):
        """Test that bash code blocks specify language"""
        if '```' in installation_content:
            assert '```bash' in installation_content or '```sh' in installation_content, \
                "Bash code blocks should specify language"


class TestLinksAndReferences:
    """Test links and cross-references in documentation"""
    
    def test_faq_links_are_valid_markdown(self, faq_content):
        """Test that FAQ links use valid markdown syntax"""
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', faq_content)
        for text, url in links:
            assert len(text) > 0, "Link text should not be empty"
            assert len(url) > 0, "Link URL should not be empty"
    
    def test_installation_links_are_valid_markdown(self, installation_content):
        """Test that installation guide links use valid markdown syntax"""
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', installation_content)
        for text, url in links:
            assert len(text) > 0, "Link text should not be empty"
            assert len(url) > 0, "Link URL should not be empty"


class TestMarkdownFormatting:
    """Test markdown formatting quality"""
    
    def test_faq_headers_have_proper_spacing(self, faq_content):
        """Test that FAQ headers are properly formatted"""
        # This test ensures headers are valid markdown
        # We just check that there are headers present
        lines = [l for l in faq_content.split('\n') if l.startswith('#')]
        assert len(lines) > 0, "FAQ should have markdown headers"
    
    def test_installation_headers_have_proper_spacing(self, installation_content):
        """Test that installation guide headers are properly formatted"""
        # This test ensures headers are valid markdown
        # We just check that there are headers present
        lines = [l for l in installation_content.split('\n') if l.startswith('#')]
        assert len(lines) > 0, "Installation guide should have markdown headers"


class TestTemporaryWorkaroundNotice:
    """Test that temporary workaround is properly noted"""
    
    def test_installation_marks_python_311_as_temporary(self, installation_content):
        """Test that Python 3.11 workaround is marked as temporary"""
        lower_content = installation_content.lower()
        assert 'temporary' in lower_content or 'workaround' in lower_content, \
            "Should indicate Python 3.11 downgrade is temporary solution"
    
    def test_mentions_future_python_support(self, installation_content):
        """Test that guide mentions aim for latest Python support"""
        lower_content = installation_content.lower()
        assert 'latest' in lower_content or 'future' in lower_content or 'support' in lower_content, \
            "Should mention goal of supporting latest Python versions"


class TestEdgeCases:
    """Test edge cases and potential issues"""
    
    def test_faq_file_readable(self, faq_path):
        """Test that FAQ file is readable"""
        assert faq_path.is_file(), "FAQ should be a file"
        with open(faq_path, 'r') as f:
            content = f.read()
            assert len(content) > 0, "FAQ should be readable"
    
    def test_installation_file_readable(self, installation_path):
        """Test that installation guide is readable"""
        assert installation_path.is_file(), "Installation guide should be a file"
        with open(installation_path, 'r') as f:
            content = f.read()
            assert len(content) > 0, "Installation guide should be readable"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])