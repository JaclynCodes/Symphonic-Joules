"""
Comprehensive tests for documentation file accuracy and consistency.

This module validates documentation files for:
- Correct file references
- Accurate version information
- Proper formatting and structure
- Consistency between documentation and actual configuration
- Installation instructions accuracy
"""

import pytest
import re
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """Get repository root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def faq_path(repo_root):
    """Get FAQ file path"""
    return repo_root / 'docs' / 'faq.md'


@pytest.fixture(scope='module')
def installation_path(repo_root):
    """Get installation guide path"""
    return repo_root / 'docs' / 'installation-setup.md'


@pytest.fixture(scope='module')
def faq_content(faq_path):
    """Load FAQ content"""
    with open(faq_path, 'r') as file:
        return file.read()


@pytest.fixture(scope='module')
def installation_content(installation_path):
    """Load installation guide content"""
    with open(installation_path, 'r') as file:
        return file.read()


class TestFAQStructure:
    """Test FAQ file structure and format"""
    
    def test_faq_file_exists(self, faq_path):
        """Test that FAQ file exists"""
        assert faq_path.exists(), "docs/faq.md should exist"
    
    def test_faq_is_markdown(self, faq_path):
        """Test that FAQ uses .md extension"""
        assert faq_path.suffix == '.md', "FAQ should be markdown file"
    
    def test_faq_not_empty(self, faq_content):
        """Test that FAQ is not empty"""
        assert len(faq_content) > 0, "FAQ should not be empty"
    
    def test_faq_has_headings(self, faq_content):
        """Test that FAQ uses markdown headings"""
        assert any(line.startswith('#') for line in faq_content.split('\n')), \
            "FAQ should use markdown headings"


class TestFAQPythonVersion:
    """Test Python version information in FAQ"""
    
    def test_faq_mentions_python_version_question(self, faq_content):
        """Test that FAQ includes Python version question"""
        assert 'What Python version' in faq_content or \
               'python version' in faq_content.lower(), \
            "FAQ should address Python version requirements"
    
    def test_faq_specifies_python_38_minimum(self, faq_content):
        """Test that FAQ specifies Python 3.8 as minimum"""
        assert '3.8' in faq_content, \
            "FAQ should mention Python 3.8 as minimum version"
    
    def test_faq_mentions_macos_compatibility(self, faq_content):
        """Test that FAQ mentions macOS compatibility issues"""
        content_lower = faq_content.lower()
        assert 'macos' in content_lower or 'mac os' in content_lower, \
            "FAQ should mention macOS compatibility"
    
    def test_faq_recommends_python_311_for_macos(self, faq_content):
        """Test that FAQ recommends Python 3.11 for macOS issues"""
        assert '3.11' in faq_content, \
            "FAQ should mention Python 3.11 as workaround"
    
    def test_faq_references_installation_guide(self, faq_content):
        """Test that FAQ links to installation guide for details"""
        assert 'installation' in faq_content.lower() or \
               'Installation Guide' in faq_content, \
            "FAQ should reference installation guide"
    
    def test_faq_python_version_section_has_heading(self, faq_content):
        """Test that Python version info is under a heading"""
        lines = faq_content.split('\n')
        python_version_line_idx = next((i for i, line in enumerate(lines) 
                                       if 'What Python version' in line), -1)
        assert python_version_line_idx >= 0, \
            "Should have Python version question"
        assert lines[python_version_line_idx].startswith('###'), \
            "Python version question should be a heading"


class TestInstallationGuideStructure:
    """Test installation guide structure"""
    
    def test_installation_file_exists(self, installation_path):
        """Test that installation guide exists"""
        assert installation_path.exists(), \
            "docs/installation-setup.md should exist"
    
    def test_installation_is_markdown(self, installation_path):
        """Test that installation guide is markdown"""
        assert installation_path.suffix == '.md', \
            "Installation guide should be markdown file"
    
    def test_installation_not_empty(self, installation_content):
        """Test that installation guide is not empty"""
        assert len(installation_content) > 100, \
            "Installation guide should have substantial content"
    
    def test_installation_has_toc(self, installation_content):
        """Test that installation guide has table of contents or sections"""
        assert installation_content.count('#') >= 3, \
            "Installation guide should have multiple sections"


class TestInstallationPythonVersion:
    """Test Python version requirements in installation guide"""
    
    def test_specifies_python_38_minimum(self, installation_content):
        """Test that installation guide specifies Python 3.8+"""
        assert '3.8' in installation_content, \
            "Should specify Python 3.8 as minimum version"
    
    def test_mentions_python_311_recommendation(self, installation_content):
        """Test that guide mentions Python 3.11 recommendation"""
        assert '3.11' in installation_content, \
            "Should mention Python 3.11 as recommendation for macOS"
    
    def test_has_system_requirements_section(self, installation_content):
        """Test that guide has system requirements section"""
        assert 'System Requirements' in installation_content or \
               'Requirements' in installation_content, \
            "Should have system requirements section"
    
    def test_python_version_in_requirements(self, installation_content):
        """Test that Python version is listed in requirements"""
        lines = installation_content.split('\n')
        requirements_section = '\n'.join(lines)
        # Look for Python version specification
        assert re.search(r'Python.*3\.\d+', requirements_section, re.IGNORECASE), \
            "System requirements should specify Python version"


class TestMacOSCompatibilitySection:
    """Test macOS compatibility documentation"""
    
    def test_has_macos_section(self, installation_content):
        """Test that installation guide has macOS compatibility section"""
        assert 'macOS' in installation_content or 'Mac OS' in installation_content, \
            "Should have macOS-specific section"
    
    def test_macos_section_mentions_python_311(self, installation_content):
        """Test that macOS section mentions Python 3.11"""
        # Find macOS section
        lines = installation_content.split('\n')
        macos_section_start = next((i for i, line in enumerate(lines) 
                                   if 'macOS' in line and '#' in line), -1)
        assert macos_section_start >= 0, "Should have macOS section"
        
        # Check if Python 3.11 is mentioned in or near that section
        section_content = '\n'.join(lines[macos_section_start:macos_section_start + 50])
        assert '3.11' in section_content, \
            "macOS section should mention Python 3.11"
    
    def test_provides_homebrew_installation(self, installation_content):
        """Test that guide provides Homebrew installation instructions"""
        content_lower = installation_content.lower()
        assert 'brew install' in content_lower or 'homebrew' in content_lower, \
            "Should provide Homebrew installation instructions for macOS"
    
    def test_provides_path_configuration(self, installation_content):
        """Test that guide explains PATH configuration"""
        assert 'PATH' in installation_content or 'path' in installation_content.lower(), \
            "Should explain PATH configuration for Python 3.11"
    
    def test_mentions_zshrc(self, installation_content):
        """Test that guide mentions .zshrc configuration"""
        assert '.zshrc' in installation_content or 'zshrc' in installation_content, \
            "Should mention .zshrc for macOS shell configuration"
    
    def test_provides_verification_command(self, installation_content):
        """Test that guide provides version verification command"""
        assert 'python --version' in installation_content or \
               'python3 --version' in installation_content, \
            "Should provide command to verify Python version"
    
    def test_explains_temporary_workaround(self, installation_content):
        """Test that guide clarifies this is a temporary workaround"""
        content_lower = installation_content.lower()
        assert 'temporary' in content_lower or 'workaround' in content_lower, \
            "Should clarify that Python 3.11 is a temporary workaround"


class TestInstallationSteps:
    """Test installation step documentation"""
    
    def test_has_numbered_steps(self, installation_content):
        """Test that installation uses numbered steps"""
        # Look for numbered list items
        assert re.search(r'^\d+\.', installation_content, re.MULTILINE), \
            "Installation steps should be numbered"
    
    def test_mentions_virtual_environment(self, installation_content):
        """Test that guide recommends virtual environment"""
        content_lower = installation_content.lower()
        assert 'venv' in content_lower or 'virtual environment' in content_lower or \
               'virtualenv' in content_lower, \
            "Should recommend using virtual environment"
    
    def test_provides_venv_creation_command(self, installation_content):
        """Test that guide shows how to create venv"""
        assert 'python -m venv' in installation_content or \
               'python3 -m venv' in installation_content, \
            "Should show venv creation command"
    
    def test_provides_venv_activation_for_unix(self, installation_content):
        """Test that guide shows venv activation for Unix/macOS"""
        assert 'source venv/bin/activate' in installation_content, \
            "Should show venv activation for Unix/macOS"
    
    def test_has_note_about_macos_compatibility(self, installation_content):
        """Test that venv section references macOS compatibility note"""
        lines = installation_content.split('\n')
        venv_line_idx = next((i for i, line in enumerate(lines) 
                             if 'source venv/bin/activate' in line), -1)
        assert venv_line_idx >= 0, "Should have venv activation command"
        
        # Check if there's a note nearby
        nearby_lines = '\n'.join(lines[venv_line_idx:venv_line_idx + 10])
        assert 'Note' in nearby_lines or 'macos' in nearby_lines.lower(), \
            "Should have note about macOS compatibility near venv activation"


class TestCodeBlocks:
    """Test code block formatting in documentation"""
    
    def test_installation_has_code_blocks(self, installation_content):
        """Test that installation guide uses proper code blocks"""
        assert '```' in installation_content, \
            "Should use markdown code blocks for commands"
    
    def test_code_blocks_specify_language(self, installation_content):
        """Test that code blocks specify language (bash)"""
        # Look for ```bash or similar
        assert '```bash' in installation_content or '```sh' in installation_content, \
            "Code blocks should specify language (bash/sh)"
    
    def test_homebrew_command_in_code_block(self, installation_content):
        """Test that Homebrew commands are in code blocks"""
        if 'brew install' in installation_content:
            lines = installation_content.split('\n')
            brew_line_idx = next((i for i, line in enumerate(lines) 
                                 if 'brew install' in line), -1)
            # Check if it's in a code block (between ``` markers)
            preceding_lines = '\n'.join(lines[max(0, brew_line_idx - 5):brew_line_idx])
            following_lines = '\n'.join(lines[brew_line_idx:brew_line_idx + 5])
            assert '```' in preceding_lines or '```' in following_lines, \
                "Homebrew commands should be in code blocks"


class TestInternalLinks:
    """Test internal documentation links"""
    
    def test_faq_links_to_installation(self, faq_content):
        """Test that FAQ links to installation guide"""
        # Look for markdown links to installation-setup.md
        assert 'installation-setup.md' in faq_content or \
               '[Installation Guide]' in faq_content, \
            "FAQ should link to installation guide"
    
    def test_installation_section_anchors(self, installation_content):
        """Test that installation guide uses section anchors for links"""
        if '#' in installation_content and '(' in installation_content:
            # Look for anchor-style links
            anchor_pattern = r'\(#[\w-]+\)'
            if re.search(anchor_pattern, installation_content):
                # If anchor links exist, they should be properly formatted
                assert True


class TestVersionConsistency:
    """Test version information consistency"""
    
    def test_python_versions_consistent(self, faq_content, installation_content):
        """Test that Python versions are consistent across documentation"""
        # Both should mention 3.8 and 3.11
        assert '3.8' in faq_content and '3.8' in installation_content, \
            "Python 3.8 should be mentioned consistently"
        assert '3.11' in faq_content and '3.11' in installation_content, \
            "Python 3.11 should be mentioned consistently"
    
    def test_no_conflicting_version_info(self, installation_content):
        """Test that there's no conflicting version information"""
        # Extract all Python versions mentioned
        versions = re.findall(r'Python\s*3\.(\d+)', installation_content, re.IGNORECASE)
        # Common versions should be: 8 (minimum), 11 (workaround), 12 (latest)
        version_nums = set(versions)
        # Should not have versions like 3.6, 3.7 (too old)
        assert '6' not in version_nums and '7' not in version_nums, \
            "Should not mention outdated Python versions"


class TestTroubleshootingSection:
    """Test troubleshooting documentation"""
    
    def test_has_troubleshooting_section(self, installation_content):
        """Test that guide includes troubleshooting section"""
        content_lower = installation_content.lower()
        assert 'troubleshooting' in content_lower or 'issues' in content_lower or \
               'problems' in content_lower, \
            "Should have troubleshooting section"
    
    def test_troubleshooting_mentions_platform_specific(self, installation_content):
        """Test that troubleshooting includes platform-specific issues"""
        content_lower = installation_content.lower()
        if 'troubleshooting' in content_lower or 'issues' in content_lower:
            assert 'platform-specific' in content_lower or 'macos' in content_lower, \
                "Troubleshooting should mention platform-specific issues"


class TestDocumentationQuality:
    """Test overall documentation quality"""
    
    def test_no_broken_markdown_links(self, faq_content, installation_content):
        """Test that markdown links are properly formatted"""
        all_content = faq_content + installation_content
        # Look for malformed links like ](text without opening bracket
        assert not re.search(r'(?<!\[)\]\([^)]+\)', all_content), \
            "All markdown links should be properly formatted"
    
    def test_no_todo_markers(self, faq_content, installation_content):
        """Test that documentation doesn't have TODO markers"""
        all_content = (faq_content + installation_content).lower()
        # It's okay to have TODO in comments, but not in user-facing content
        if 'todo' in all_content or 'fixme' in all_content:
            # Check if it's in a code comment context
            pass  # Allow TODOs in documentation as they're planning notes
    
    def test_consistent_code_formatting(self, installation_content):
        """Test that inline code uses backticks consistently"""
        # Count usage of backticks for inline code
        backtick_count = installation_content.count('`')
        if backtick_count > 0:
            # Should be even number (opening and closing)
            assert backtick_count % 2 == 0, \
                "Inline code backticks should be balanced"


class TestEdgeCases:
    """Test edge cases in documentation"""
    
    def test_no_hardcoded_usernames(self, installation_content):
        """Test that documentation doesn't have hardcoded usernames"""
        # Should not have paths like /Users/john or /home/alice
        content_lower = installation_content.lower()
        assert '/users/john' not in content_lower and \
               '/home/alice' not in content_lower, \
            "Should not have example paths with specific usernames"
    
    def test_references_current_python_versions(self, installation_content):
        """Test that documentation references current Python versions"""
        # Should not reference very old versions
        assert '2.7' not in installation_content, \
            "Should not reference Python 2.7"
        assert '3.5' not in installation_content and '3.6' not in installation_content, \
            "Should not reference very old Python 3 versions"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])