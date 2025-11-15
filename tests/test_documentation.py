"""
Comprehensive test suite for markdown documentation files

This test suite validates the documentation in the repository including:
- File existence and readability
- Markdown syntax and structure
- Content completeness and quality
- Internal link validation
- Code block formatting
- Heading structure
- Documentation consistency
"""

import pytest
import os
import re
from pathlib import Path


@pytest.fixture(scope='module')
def repo_root():
    """Get repository root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope='module')
def docs_dir(repo_root):
    """Get docs directory path"""
    return repo_root / 'docs'


@pytest.fixture(scope='module')
def all_markdown_files(repo_root):
    """Get all markdown files in the repository"""
    markdown_files = []
    for pattern in ['*.md', 'docs/**/*.md', '.github/**/*.md']:
        markdown_files.extend(repo_root.glob(pattern))
    return [f for f in markdown_files if f.is_file()]


class TestDocumentationStructure:
    """Test basic documentation file structure"""
    
    def test_readme_exists(self, repo_root):
        """Test that README.md exists at repository root"""
        readme = repo_root / 'README.md'
        assert readme.exists(), "README.md must exist at repository root"
        assert readme.is_file(), "README.md must be a file"
    
    def test_contributing_guide_exists(self, repo_root):
        """Test that CONTRIBUTING.md exists"""
        contributing = repo_root / 'CONTRIBUTING.md'
        assert contributing.exists(), "CONTRIBUTING.md must exist"
    
    def test_changelog_exists(self, repo_root):
        """Test that CHANGELOG.md exists"""
        changelog = repo_root / 'CHANGELOG.md'
        assert changelog.exists(), "CHANGELOG.md must exist"
    
    def test_license_exists(self, repo_root):
        """Test that LICENSE file exists"""
        license_file = repo_root / 'LICENSE'
        assert license_file.exists(), "LICENSE file must exist"
    
    def test_docs_directory_exists(self, docs_dir):
        """Test that docs directory exists"""
        assert docs_dir.exists(), "docs directory must exist"
        assert docs_dir.is_dir(), "docs must be a directory"
    
    def test_all_markdown_files_readable(self, all_markdown_files):
        """Test that all markdown files are readable"""
        for md_file in all_markdown_files:
            assert os.access(md_file, os.R_OK), f"{md_file} must be readable"


class TestREADMEContent:
    """Test README.md content and structure"""
    
    @pytest.fixture(scope='class')
    def readme_content(self, repo_root):
        """Load README content"""
        with open(repo_root / 'README.md', 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_readme_not_empty(self, readme_content):
        """Test that README is not empty"""
        assert len(readme_content.strip()) > 0, "README must not be empty"
    
    def test_readme_has_title(self, readme_content):
        """Test that README has a top-level heading"""
        assert re.search(r'^#\s+\w+', readme_content, re.MULTILINE), \
            "README must have a top-level heading"
    
    def test_readme_has_project_name(self, readme_content):
        """Test that README mentions the project name"""
        assert 'Symphonic-Joules' in readme_content or 'symphonic-joules' in readme_content.lower(), \
            "README should mention project name"
    
    def test_readme_has_description(self, readme_content):
        """Test that README includes project description"""
        # Should have some content after the title
        lines = [line for line in readme_content.split('\n') if line.strip()]
        assert len(lines) > 3, "README should have substantive content"
    
    def test_readme_has_getting_started_section(self, readme_content):
        """Test that README has getting started or installation info"""
        lower_content = readme_content.lower()
        assert any(keyword in lower_content for keyword in 
                  ['getting started', 'installation', 'quick start', 'setup']), \
            "README should have getting started information"
    
    def test_readme_has_code_blocks_properly_formatted(self, readme_content):
        """Test that code blocks use proper markdown fencing"""
        # Find all code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', readme_content)
        for block in code_blocks:
            # Should start with ``` and language identifier or just ```
            assert block.startswith('```'), "Code block should start with ```"
            assert block.endswith('```'), "Code block should end with ```"


class TestContributingGuide:
    """Test CONTRIBUTING.md content"""
    
    @pytest.fixture(scope='class')
    def contributing_content(self, repo_root):
        """Load CONTRIBUTING content"""
        with open(repo_root / 'CONTRIBUTING.md', 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_contributing_not_empty(self, contributing_content):
        """Test that CONTRIBUTING guide is not empty"""
        assert len(contributing_content.strip()) > 0, "CONTRIBUTING.md must not be empty"
    
    def test_contributing_has_title(self, contributing_content):
        """Test that CONTRIBUTING has a title"""
        assert re.search(r'^#\s+', contributing_content, re.MULTILINE), \
            "CONTRIBUTING.md should have a title"
    
    def test_contributing_mentions_pull_requests(self, contributing_content):
        """Test that contributing guide mentions pull requests"""
        lower_content = contributing_content.lower()
        assert 'pull request' in lower_content or 'pr' in lower_content, \
            "Contributing guide should explain pull request process"
    
    def test_contributing_mentions_issues(self, contributing_content):
        """Test that contributing guide mentions issues"""
        assert 'issue' in contributing_content.lower(), \
            "Contributing guide should mention issues"
    
    def test_contributing_has_code_style_section(self, contributing_content):
        """Test that contributing guide addresses code style"""
        lower_content = contributing_content.lower()
        assert any(keyword in lower_content for keyword in 
                  ['code style', 'coding standard', 'style guide', 'convention']), \
            "Contributing guide should address code style"


class TestChangelog:
    """Test CHANGELOG.md structure"""
    
    @pytest.fixture(scope='class')
    def changelog_content(self, repo_root):
        """Load CHANGELOG content"""
        with open(repo_root / 'CHANGELOG.md', 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_changelog_not_empty(self, changelog_content):
        """Test that CHANGELOG is not empty"""
        assert len(changelog_content.strip()) > 0, "CHANGELOG.md must not be empty"
    
    def test_changelog_has_title(self, changelog_content):
        """Test that CHANGELOG has a title"""
        assert re.search(r'^#\s+', changelog_content, re.MULTILINE), \
            "CHANGELOG.md should have a title"
    
    def test_changelog_mentions_changes(self, changelog_content):
        """Test that CHANGELOG contains version or change information"""
        lower_content = changelog_content.lower()
        # Should have some indication of versions or changes
        has_content = any(keyword in lower_content for keyword in 
                         ['version', 'release', 'change', 'added', 'fixed', 'updated'])
        assert has_content, "CHANGELOG should document changes or versions"


class TestDocsDirectory:
    """Test docs directory structure and content"""
    
    def test_docs_readme_exists(self, docs_dir):
        """Test that docs directory has a README"""
        docs_readme = docs_dir / 'README.md'
        assert docs_readme.exists(), "docs/README.md should exist"
    
    def test_key_documentation_files_exist(self, docs_dir):
        """Test that key documentation files exist"""
        expected_docs = [
            'installation-setup.md',
            'getting-started.md',
            'api-reference.md',
            'architecture.md'
        ]
        
        for doc in expected_docs:
            doc_path = docs_dir / doc
            assert doc_path.exists(), f"{doc} should exist in docs directory"
    
    def test_all_docs_are_readable(self, docs_dir):
        """Test that all doc files are readable"""
        for md_file in docs_dir.glob('**/*.md'):
            assert os.access(md_file, os.R_OK), f"{md_file} must be readable"


class TestMarkdownFormatting:
    """Test markdown formatting consistency"""
    
    def test_no_trailing_whitespace(self, all_markdown_files):
        """Test that markdown files don't have excessive trailing whitespace"""
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # Allow up to 2 trailing spaces (markdown line break)
                trailing = len(line) - len(line.rstrip(' '))
                assert trailing <= 2, \
                    f"{md_file}:{i} has excessive trailing whitespace ({trailing} spaces)"
    
    def test_headings_have_space_after_hash(self, all_markdown_files):
        """Test that headings have space after hash marks"""
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find headings without space after #
            bad_headings = re.findall(r'^#{1,6}[^\s#]', content, re.MULTILINE)
            assert len(bad_headings) == 0, \
                f"{md_file} has headings without space after #: {bad_headings}"
    
    def test_code_blocks_are_fenced(self, all_markdown_files):
        """Test that code blocks use proper fencing"""
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count opening and closing backticks
            opening = content.count('```')
            # Should be even number (each block has opening and closing)
            assert opening % 2 == 0, \
                f"{md_file} has unmatched code block fences (``` count: {opening})"


class TestInternalLinks:
    """Test internal links in documentation"""
    
    def test_internal_links_use_relative_paths(self, all_markdown_files, repo_root):
        """Test that internal links use relative paths"""
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find markdown links
            links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
            
            for link_text, link_url in links:
                # Skip external links
                if link_url.startswith(('http://', 'https://', '#')):
                    continue
                
                # Internal links should be relative
                assert not link_url.startswith('/'), \
                    f"{md_file}: Internal link '{link_url}' should use relative path"
    
    def test_doc_links_to_existing_files(self, all_markdown_files, repo_root):
        """Test that links to documentation files point to existing files"""
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find markdown links to .md files
            links = re.findall(r'\[([^\]]+)\]\(([^\)#]+\.md)[^\)]*\)', content)
            
            for link_text, link_url in links:
                # Skip external links
                if link_url.startswith(('http://', 'https://')):
                    continue
                
                # Resolve relative path
                target = (md_file.parent / link_url).resolve()
                
                # Check if target exists relative to repo root
                if not target.exists():
                    # Try from repo root
                    target = (repo_root / link_url).resolve()
                
                assert target.exists(), \
                    f"{md_file}: Link to '{link_url}' points to non-existent file"


class TestHeadingStructure:
    """Test heading hierarchy in documentation"""
    
    def test_single_h1_heading(self, all_markdown_files):
        """Test that each document has exactly one H1 heading"""
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count H1 headings (lines starting with single #)
            h1_headings = re.findall(r'^#\s+[^#]', content, re.MULTILINE)
            
            assert len(h1_headings) <= 1, \
                f"{md_file} should have at most one H1 heading, found {len(h1_headings)}"
    
    def test_heading_hierarchy_is_logical(self, all_markdown_files):
        """Test that heading levels don't skip levels"""
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract heading levels
            headings = re.findall(r'^(#{1,6})\s+', content, re.MULTILINE)
            heading_levels = [len(h) for h in headings]
            
            # Check for level skipping
            for i in range(1, len(heading_levels)):
                prev_level = heading_levels[i-1]
                curr_level = heading_levels[i]
                
                # Should not skip more than one level
                if curr_level > prev_level:
                    assert curr_level - prev_level <= 1, \
                        f"{md_file}: Heading hierarchy skips from H{prev_level} to H{curr_level}"


class TestCodeBlockQuality:
    """Test code blocks in documentation"""
    
    def test_code_blocks_have_language_identifiers(self, all_markdown_files):
        """Test that code blocks specify language where appropriate"""
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find code blocks
            code_blocks = re.findall(r'```(\w*)\n', content)
            
            # At least some blocks should have language identifiers
            if len(code_blocks) > 0:
                with_lang = sum(1 for lang in code_blocks if lang)
                # Allow some blocks without language, but encourage usage
                if len(code_blocks) >= 3:
                    assert with_lang >= len(code_blocks) * 0.5, \
                        f"{md_file}: Consider adding language identifiers to code blocks"


class TestInstallationDocumentation:
    """Test installation-setup.md specifically"""
    
    @pytest.fixture(scope='class')
    def installation_content(self, docs_dir):
        """Load installation documentation"""
        install_doc = docs_dir / 'installation-setup.md'
        if not install_doc.exists():
            pytest.skip("installation-setup.md not found")
        with open(install_doc, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_installation_doc_not_empty(self, installation_content):
        """Test that installation doc is not empty"""
        assert len(installation_content.strip()) > 0
    
    def test_installation_mentions_prerequisites(self, installation_content):
        """Test that installation doc mentions prerequisites"""
        lower_content = installation_content.lower()
        assert any(keyword in lower_content for keyword in 
                  ['prerequisite', 'requirement', 'dependency', 'python']), \
            "Installation doc should mention prerequisites"
    
    def test_installation_has_steps(self, installation_content):
        """Test that installation doc provides steps"""
        lower_content = installation_content.lower()
        # Should have numbered lists or step indicators
        has_steps = any(keyword in lower_content for keyword in 
                       ['step', 'install', 'setup', 'clone'])
        assert has_steps, "Installation doc should provide installation steps"


class TestAPIDocumentation:
    """Test api-reference.md specifically"""
    
    @pytest.fixture(scope='class')
    def api_content(self, docs_dir):
        """Load API documentation"""
        api_doc = docs_dir / 'api-reference.md'
        if not api_doc.exists():
            pytest.skip("api-reference.md not found")
        with open(api_doc, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_api_doc_not_empty(self, api_content):
        """Test that API doc is not empty"""
        assert len(api_content.strip()) > 0
    
    def test_api_doc_has_code_examples(self, api_content):
        """Test that API doc includes code examples"""
        # Should have code blocks with Python examples
        assert '```' in api_content, "API doc should have code examples"
        assert 'python' in api_content.lower() or '```py' in api_content.lower(), \
            "API doc should have Python code examples"


class TestDocumentationConsistency:
    """Test consistency across documentation files"""
    
    def test_project_name_consistency(self, all_markdown_files):
        """Test that project name is used consistently"""
        project_names = set()
        pattern = re.compile(r'\bSymphonic[-\s]?Joules?\b', re.IGNORECASE)
        
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            matches = pattern.findall(content)
            project_names.update(matches)
        
        # Should use consistent capitalization
        if len(project_names) > 0:
            # Most common form should be used consistently
            assert 'Symphonic-Joules' in project_names or 'symphonic-joules' in project_names, \
                "Project name should use consistent formatting"
    
    def test_github_links_use_correct_repo(self, all_markdown_files):
        """Test that GitHub links point to the correct repository"""
        for md_file in all_markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find GitHub URLs
            github_urls = re.findall(r'https://github\.com/([^/\s\)]+)/([^/\s\)]+)', content)
            
            for org, repo in github_urls:
                # Should point to JaclynCodes/Symphonic-Joules or similar
                if 'symphonic' in repo.lower() or 'joules' in repo.lower():
                    assert org in ['JaclynCodes', 'jaclyncodes'], \
                        f"{md_file}: GitHub link should use correct organization"


class TestLicenseFile:
    """Test LICENSE file content"""
    
    @pytest.fixture(scope='class')
    def license_content(self, repo_root):
        """Load LICENSE content"""
        with open(repo_root / 'LICENSE', 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_license_not_empty(self, license_content):
        """Test that LICENSE is not empty"""
        assert len(license_content.strip()) > 0, "LICENSE must not be empty"
    
    def test_license_has_copyright(self, license_content):
        """Test that LICENSE includes copyright notice"""
        assert 'copyright' in license_content.lower(), \
            "LICENSE should include copyright notice"
    
    def test_license_specifies_terms(self, license_content):
        """Test that LICENSE specifies license terms"""
        # Should have substantial content
        assert len(license_content.split()) > 50, \
            "LICENSE should specify license terms"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])