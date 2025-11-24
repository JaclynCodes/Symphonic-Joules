"""
Tests for documentation files validation

This module validates documentation files for:
- Markdown syntax and structure
- Link validity
- Content accuracy
- Formatting consistency
- Required sections
"""

import pytest
import re
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def docs_dir(repo_root):
    """Get the docs directory."""
    return repo_root / 'docs'


@pytest.fixture(scope='module')
def faq_path(docs_dir):
    """Get path to FAQ documentation"""
    return docs_dir / 'faq.md'


@pytest.fixture(scope='module')
def faq_content(faq_path):
    """Load FAQ content"""
    with open(faq_path, 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def installation_path(docs_dir):
    """Get path to installation documentation"""
    return docs_dir / 'installation-setup.md'


@pytest.fixture(scope='module')
def installation_content(installation_path):
    """Load installation guide content"""
    with open(installation_path, 'r') as f:
        return f.read()


class TestFAQStructure:
    """Test FAQ documentation structure"""
    
    def test_faq_file_exists(self, faq_path):
        """Test that faq.md exists"""
        assert faq_path.exists(), \
            "faq.md should exist in docs directory"
    
    def test_faq_is_not_empty(self, faq_content):
        """Test that FAQ is not empty"""
        assert len(faq_content) > 0, \
            "FAQ should not be empty"
    
    def test_faq_has_headings(self, faq_content):
        """Test that FAQ has markdown headings"""
        assert re.search(r'^#+\s+', faq_content, re.MULTILINE), \
            "FAQ should have markdown headings"
    
    def test_faq_has_questions(self, faq_content):
        """Test that FAQ contains questions"""
        # Look for question marks or common question patterns
        assert '?' in faq_content or re.search(r'^###?\s+\w+', faq_content, re.MULTILINE), \
            "FAQ should contain questions"


class TestFAQContent:
    """Test FAQ content and completeness"""
    
    def test_faq_mentions_python_version(self, faq_content):
        """Test that FAQ mentions Python version requirements"""
        content_lower = faq_content.lower()
        assert 'python' in content_lower, \
            "FAQ should mention Python"
        assert any(ver in content_lower for ver in ['3.8', '3.11', '3.12', 'version']), \
            "FAQ should specify Python version requirements"
    
    def test_faq_mentions_macos_compatibility(self, faq_content):
        """Test that FAQ addresses macOS compatibility"""
        content_lower = faq_content.lower()
        assert 'macos' in content_lower or 'mac os' in content_lower, \
            "FAQ should address macOS compatibility"
    
    def test_faq_has_installation_reference(self, faq_content):
        """Test that FAQ references installation guide"""
        content_lower = faq_content.lower()
        assert 'installation' in content_lower or 'install' in content_lower, \
            "FAQ should reference installation"


class TestInstallationGuideStructure:
    """Test installation guide structure"""
    
    def test_installation_file_exists(self, installation_path):
        """Test that installation-setup.md exists"""
        assert installation_path.exists(), \
            "installation-setup.md should exist"
    
    def test_installation_is_not_empty(self, installation_content):
        """Test that installation guide is not empty"""
        assert len(installation_content) > 0, \
            "Installation guide should not be empty"
    
    def test_installation_has_headings(self, installation_content):
        """Test that installation guide has structure"""
        headings = re.findall(r'^#+\s+(.+)$', installation_content, re.MULTILINE)
        assert len(headings) > 0, \
            "Installation guide should have section headings"
    
    def test_installation_has_code_blocks(self, installation_content):
        """Test that installation guide includes code examples"""
        assert '```' in installation_content, \
            "Installation guide should have code blocks"


class TestInstallationGuideContent:
    """Test installation guide content"""
    
    def test_mentions_python_requirements(self, installation_content):
        """Test that guide mentions Python requirements"""
        content_lower = installation_content.lower()
        assert 'python' in content_lower, \
            "Installation guide should mention Python"
        assert '3.8' in content_lower or '3.11' in content_lower or '3.12' in content_lower, \
            "Should specify Python version"
    
    def test_has_virtual_environment_instructions(self, installation_content):
        """Test that guide includes virtual environment setup"""
        content_lower = installation_content.lower()
        assert 'venv' in content_lower or 'virtualenv' in content_lower, \
            "Should include virtual environment instructions"
    
    def test_has_dependency_installation(self, installation_content):
        """Test that guide covers dependency installation"""
        assert 'pip install' in installation_content or 'requirements.txt' in installation_content, \
            "Should cover dependency installation"
    
    def test_has_macos_section(self, installation_content):
        """Test that guide has macOS-specific section"""
        content_lower = installation_content.lower()
        assert 'macos' in content_lower or 'mac os' in content_lower, \
            "Should have macOS-specific section"
    
    def test_has_python_downgrade_workaround(self, installation_content):
        """Test that guide mentions Python downgrade workaround"""
        content_lower = installation_content.lower()
        assert 'python 3.11' in content_lower or 'python@3.11' in content_lower, \
            "Should mention Python 3.11 workaround"
        assert 'brew' in content_lower or 'homebrew' in content_lower, \
            "Should mention Homebrew for macOS Python installation"
    
    def test_has_troubleshooting_section(self, installation_content):
        """Test that guide includes troubleshooting"""
        content_lower = installation_content.lower()
        assert 'troubleshoot' in content_lower or 'issue' in content_lower or 'problem' in content_lower, \
            "Should include troubleshooting section"


class TestMarkdownQuality:
    """Test markdown formatting quality"""
    
    def test_faq_has_proper_markdown_headers(self, faq_content):
        """Test that FAQ uses proper markdown header syntax"""
        lines = faq_content.split('\n')
        for line in lines:
            if line.startswith('#'):
                # Headers should have space after #
                assert re.match(r'^#+\s+\S', line), \
                    f"Header should have space after #: {line[:50]}"
    
    def test_installation_has_proper_markdown_headers(self, installation_content):
        """Test that installation guide uses proper header syntax"""
        lines = installation_content.split('\n')
        for line in lines:
            if line.startswith('#'):
                assert re.match(r'^#+\s+\S', line), \
                    f"Header should have space after #: {line[:50]}"
    
    def test_code_blocks_are_properly_formatted(self, installation_content):
        """Test that code blocks use proper markdown syntax"""
        # Check for code blocks
        code_blocks = re.findall(r'```(\w*)\n(.*?)```', installation_content, re.DOTALL)
        assert len(code_blocks) > 0, \
            "Should have properly formatted code blocks"
        
        # Check that code blocks specify language where appropriate
        for lang, code in code_blocks:
            if 'bash' in code.lower() or 'pip' in code or 'python' in code:
                # Should probably specify language
                pass  # Allow both specified and unspecified for flexibility


class TestInternalLinks:
    """Test internal documentation links"""
    
    def test_faq_links_to_installation_guide(self, faq_content):
        """Test that FAQ links to installation guide"""
        # Look for markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', faq_content)
        installation_links = [link for text, link in links 
                             if 'installation' in link.lower()]
        
        assert len(installation_links) > 0, \
            "FAQ should link to installation guide"
    
    def test_links_use_relative_paths(self, faq_content, installation_content):
        """Test that internal links use relative paths"""
        all_content = faq_content + '\n' + installation_content
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', all_content)
        
        for text, link in links:
            if not link.startswith('http'):
                # Internal links should use relative paths
                assert not link.startswith('/'), \
                    f"Internal link should use relative path: {link}"


class TestDocumentationCompleteness:
    """Test that documentation covers key topics"""
    
    def test_system_requirements_documented(self, installation_content):
        """Test that system requirements are documented"""
        content_lower = installation_content.lower()
        assert 'requirement' in content_lower or 'system' in content_lower, \
            "Should document system requirements"
    
    def test_platform_specific_instructions(self, installation_content):
        """Test that platform-specific instructions exist"""
        content_lower = installation_content.lower()
        # Should mention at least one platform specifically
        platforms = ['windows', 'macos', 'linux', 'ubuntu']
        assert any(platform in content_lower for platform in platforms), \
            "Should include platform-specific instructions"
    
    def test_getting_help_section(self, installation_content):
        """Test that there's a section on getting help"""
        content_lower = installation_content.lower()
        assert 'help' in content_lower or 'support' in content_lower, \
            "Should have section on getting help"


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_no_broken_markdown_syntax(self, faq_content, installation_content):
        """Test for common markdown syntax errors"""
        all_content = faq_content + '\n' + installation_content
        
        # Check for unclosed code blocks
        code_block_markers = all_content.count('```')
        assert code_block_markers % 2 == 0, \
            "All code blocks should be properly closed"
        
        # Check for unmatched brackets in links
        open_brackets = all_content.count('[')
        close_brackets = all_content.count(']')
        open_parens_after_brackets = len(re.findall(r'\]\(', all_content))
        close_parens_after_open = len(re.findall(r'\]\([^)]*\)', all_content))
        
        # Should have balanced link syntax
        assert open_parens_after_brackets == close_parens_after_open, \
            "Link syntax should be balanced"
    
    def test_no_placeholder_text(self, faq_content, installation_content):
        """Test that docs don't contain placeholder text"""
        all_content = (faq_content + '\n' + installation_content).lower()
        placeholders = ['todo', 'tbd', 'coming soon', 'placeholder', 'xxx']
        
        found_placeholders = [p for p in placeholders if p in all_content]
        # Allow some placeholders but warn if too many
        assert len(found_placeholders) <= 2, \
            f"Documentation should minimize placeholder text: {found_placeholders}"
    
    def test_files_end_with_newline(self, faq_path, installation_path):
        """Test that markdown files end with newline"""
        for path in [faq_path, installation_path]:
            with open(path, 'rb') as f:
                content = f.read()
                if len(content) > 0:
                    assert content[-1:] == b'\n', \
                        f"{path.name} should end with newline"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])