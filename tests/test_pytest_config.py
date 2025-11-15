























































































































































































































































































































































































































if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

# ============================================================================
# ADDITIONAL COMPREHENSIVE TESTS - Enhanced Coverage
# ============================================================================

@pytest.mark.unit
class TestParametrizedConfigValidation:
    """Parametrized tests for comprehensive config validation"""
    
    @pytest.mark.parametrize("option_name,expected_in_value", [
        ("testpaths", "tests"),
        ("python_files", "test_"),
        ("python_files", ".py"),
        ("python_classes", "Test"),
        ("python_functions", "test_"),
    ])
    def test_required_options_root_config(self, root_config_content, option_name, expected_in_value):
        """Parametrized test for required options in root config"""
        assert root_config_content.has_option('pytest', option_name), \
            f"Root config missing required option '{option_name}'"
        value = root_config_content.get('pytest', option_name)
        assert expected_in_value in value, \
            f"Expected '{expected_in_value}' in {option_name}, got '{value}'"
    
    @pytest.mark.parametrize("option_name,expected_in_value", [
        ("testpaths", "tests"),
        ("python_files", "test_"),
        ("python_classes", "Test"),
        ("python_functions", "test_"),
    ])
    def test_required_options_tests_config(self, tests_config_content, option_name, expected_in_value):
        """Parametrized test for required options in tests config"""
        assert tests_config_content.has_option('pytest', option_name), \
            f"Tests config missing required option '{option_name}'"
        value = tests_config_content.get('pytest', option_name)
        assert expected_in_value in value, \
            f"Expected '{expected_in_value}' in {option_name}, got '{value}'"
    
    @pytest.mark.parametrize("flag", ["-v", "--tb"])
    def test_addopts_contains_flags(self, root_config_content, flag):
        """Parametrized test for addopts flags"""
        addopts = root_config_content.get('pytest', 'addopts')
        assert flag in addopts, f"Expected flag '{flag}' in addopts"
    
    @pytest.mark.parametrize("marker_name", ["workflows", "integration", "unit"])
    def test_all_required_markers_defined(self, tests_config_content, marker_name):
        """Parametrized test for marker definitions"""
        markers = tests_config_content.get('pytest', 'markers')
        assert marker_name in markers, f"Marker '{marker_name}' not defined in tests config"
    
    @pytest.mark.parametrize("pattern,description", [
        ("test_*.py", "matches test files starting with test_"),
        ("Test*", "matches test classes starting with Test"),
        ("test_*", "matches test functions starting with test_"),
    ])
    def test_naming_patterns_are_standard(self, root_config_content, pattern, description):
        """Parametrized test for standard pytest naming patterns"""
        config_str = str(root_config_content._sections)
        assert pattern in config_str, f"Standard pattern '{pattern}' not found ({description})"


@pytest.mark.unit
class TestNegativeConfigScenarios:
    """Test error conditions and invalid configurations"""
    
    def test_config_rejects_invalid_path_if_modified(self, repo_root):
        """Test that ConfigParser would reject malformed config"""
        # This tests our understanding of what would be invalid
        invalid_config = "[pytest]\ntestpaths tests"  # Missing = sign
        parser = configparser.ConfigParser()
        
        # Should raise if we try to parse invalid config
        with pytest.raises(configparser.MissingSectionHeaderError):
            parser.read_string("testpaths = tests")  # No section header
    
    def test_empty_config_section_detection(self):
        """Test detection of empty config sections"""
        parser = configparser.ConfigParser()
        parser.read_string("[pytest]\n")
        
        # Empty section should have no options
        assert len(parser.options('pytest')) == 0, "Empty section should have no options"
    
    def test_config_handles_missing_file_gracefully(self, repo_root):
        """Test that parser handles non-existent file gracefully"""
        parser = configparser.ConfigParser()
        non_existent = repo_root / 'nonexistent.ini'
        
        # Should not raise, just return empty list
        result = parser.read(non_existent)
        assert len(result) == 0, "Parser should return empty list for missing file"
    
    def test_duplicate_option_handling(self):
        """Test that duplicate options are handled (last value wins)"""
        parser = configparser.ConfigParser()
        config_with_dup = """[pytest]
testpaths = first
testpaths = second
"""
        parser.read_string(config_with_dup)
        value = parser.get('pytest', 'testpaths')
        assert value == 'second', "Last value should win with duplicate options"
    
    def test_invalid_marker_format_detection(self, tests_config_content):
        """Test that markers have proper format with descriptions"""
        markers = tests_config_content.get('pytest', 'markers')
        marker_lines = [line.strip() for line in markers.split('\n') if line.strip()]
        
        for marker_line in marker_lines:
            if ':' not in marker_line:
                pytest.fail(f"Marker '{marker_line}' missing description (should have ':')")


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for config interaction with pytest"""
    
    def test_configs_are_discoverable_by_pytest(self, repo_root):
        """Test that pytest would discover these config files"""
        # Pytest looks for pytest.ini in current directory and parent directories
        root_config = repo_root / 'pytest.ini'
        tests_config = repo_root / 'tests' / 'pytest.ini'
        
        assert root_config.exists(), "Root config must exist for pytest discovery"
        assert tests_config.exists(), "Tests config must exist"
        
        # Both should be in valid locations
        assert root_config.parent == repo_root
        assert tests_config.parent == repo_root / 'tests'
    
    def test_testpaths_directory_actually_exists(self, root_config_content, repo_root):
        """Test that configured testpaths directory exists"""
        testpaths = root_config_content.get('pytest', 'testpaths')
        test_dir = repo_root / testpaths
        
        assert test_dir.exists(), f"Configured testpaths directory '{testpaths}' does not exist"
        assert test_dir.is_dir(), f"Configured testpaths '{testpaths}' is not a directory"
    
    def test_marker_strictness_prevents_typos(self, tests_config_content):
        """Test that --strict-markers is enabled to catch marker typos"""
        addopts = tests_config_content.get('pytest', 'addopts')
        assert '--strict-markers' in addopts, \
            "Should use --strict-markers to prevent typos in marker names"
    
    def test_configs_use_compatible_options(self, root_config_content, tests_config_content):
        """Test that both configs use compatible pytest options"""
        # Both should have same core options
        core_options = ['testpaths', 'python_files', 'python_classes', 'python_functions']
        
        for option in core_options:
            assert root_config_content.has_option('pytest', option), \
                f"Root config missing core option '{option}'"
            assert tests_config_content.has_option('pytest', option), \
                f"Tests config missing core option '{option}'"
    
    def test_verbose_mode_consistency(self, root_config_content, tests_config_content):
        """Test that both configs enable verbose output consistently"""
        root_addopts = root_config_content.get('pytest', 'addopts')
        tests_addopts = tests_config_content.get('pytest', 'addopts')
        
        assert '-v' in root_addopts and '-v' in tests_addopts, \
            "Both configs should enable verbose mode with -v flag"


@pytest.mark.unit
class TestConfigFileContent:
    """Test actual content and format of config files"""
    
    def test_config_uses_ini_format(self, root_config_path):
        """Test that config file is valid INI format"""
        content = root_config_path.read_text()
        
        # Must have section header
        assert '[' in content and ']' in content, "Config must have INI section headers"
        
        # Check for proper section format
        assert '[pytest]' in content or '[tool:pytest]' in content, \
            "Config must have [pytest] section"
    
    def test_no_conflicting_options(self, root_config_content):
        """Test that config doesn't have conflicting options"""
        # Get all options in pytest section
        options = root_config_content.options('pytest')
        
        # Check for known conflicts
        if 'testpaths' in options:
            value = root_config_content.get('pytest', 'testpaths')
            # Shouldn't have multiple conflicting paths
            assert value.count('/') < 5, "testpaths should be simple, not deeply nested"
    
    def test_addopts_format_is_parseable(self, root_config_content):
        """Test that addopts can be parsed as command line arguments"""
        addopts = root_config_content.get('pytest', 'addopts')
        
        # Should not have malformed options
        assert not addopts.startswith(' '), "addopts should not start with space"
        assert not addopts.endswith(' ' * 3), "addopts should not have excessive trailing spaces"
        
        # Common flags should be well-formed
        if '--tb' in addopts:
            assert '--tb=' in addopts or '--tb ' in addopts, \
                "traceback flag should be well-formed (--tb=value or --tb value)"
    
    def test_markers_have_proper_descriptions(self, tests_config_content):
        """Test that each marker has a meaningful description"""
        markers = tests_config_content.get('pytest', 'markers')
        marker_lines = [line.strip() for line in markers.split('\n') if line.strip()]
        
        for marker_line in marker_lines:
            if ':' in marker_line:
                name, desc = marker_line.split(':', 1)
                assert len(desc.strip()) > 0, f"Marker '{name}' has empty description"
                assert len(desc.strip()) > 5, f"Marker '{name}' description too short"
    
    def test_config_has_reasonable_line_count(self, root_config_path):
        """Test that config file is not excessively long"""
        lines = root_config_path.read_text().split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Config should be concise but not empty
        assert 3 <= len(non_empty_lines) <= 50, \
            f"Config should be concise (3-50 lines), got {len(non_empty_lines)}"
    
    @pytest.mark.parametrize("encoding", ["utf-8", "ascii"])
    def test_config_file_encoding(self, root_config_path, encoding):
        """Test that config file uses standard encoding"""
        try:
            content = root_config_path.read_text(encoding=encoding)
            assert len(content) > 0, f"Config should be readable in {encoding}"
        except UnicodeDecodeError:
            if encoding == "ascii":
                # UTF-8 is acceptable even if not pure ASCII
                pass
            else:
                pytest.fail(f"Config should be readable in {encoding}")


@pytest.mark.unit
class TestAdvancedConfigurationFeatures:
    """Test advanced pytest configuration features"""
    
    def test_traceback_style_improves_readability(self, root_config_content):
        """Test that traceback style is configured for better output"""
        addopts = root_config_content.get('pytest', 'addopts')
        
        if '--tb' in addopts:
            # Should use short, long, or auto (not native or line which are harder to read)
            assert any(style in addopts for style in ['--tb=short', '--tb=auto', '--tb=long']), \
                "Should use readable traceback style"
    
    def test_no_deprecated_configuration_keys(self, root_config_content):
        """Test that config doesn't use deprecated pytest configuration"""
        deprecated_options = [
            'junit_suite_name',  # Use junit_family instead
            'doctest_optionflags',  # Deprecated in favor of other options
        ]
        
        for option in deprecated_options:
            if root_config_content.has_option('pytest', option):
                pytest.fail(f"Config uses deprecated option '{option}'")
    
    def test_marker_registration_completeness(self, tests_config_content):
        """Test that all used markers are registered"""
        markers = tests_config_content.get('pytest', 'markers')
        
        # Should have the common marker types
        expected_markers = ['unit', 'integration']
        for marker in expected_markers:
            assert marker in markers, f"Common marker '{marker}' should be registered"
    
    def test_config_section_is_pytest_not_tool(self, root_config_content):
        """Test that config uses [pytest] not [tool:pytest] for pytest.ini"""
        # pytest.ini should use [pytest], pyproject.toml uses [tool.pytest.ini_options]
        assert root_config_content.has_section('pytest'), \
            "pytest.ini should use [pytest] section"
        assert not root_config_content.has_section('tool:pytest'), \
            "pytest.ini should not use [tool:pytest] section (that's for pyproject.toml)"


@pytest.mark.unit
class TestCrossConfigConsistency:
    """Test consistency across both configuration files"""
    
    @pytest.mark.parametrize("option", [
        "testpaths",
        "python_files", 
        "python_classes",
        "python_functions"
    ])
    def test_critical_options_match_exactly(self, root_config_content, tests_config_content, option):
        """Parametrized test that critical options match between configs"""
        root_value = root_config_content.get('pytest', option)
        tests_value = tests_config_content.get('pytest', option)
        
        assert root_value == tests_value, \
            f"Mismatch in '{option}': root='{root_value}' vs tests='{tests_value}'"
    
    def test_both_configs_are_valid_ini(self, root_config_path, tests_config_path):
        """Test that both configs are valid INI files"""
        for config_path in [root_config_path, tests_config_path]:
            parser = configparser.ConfigParser()
            try:
                parser.read(config_path)
                assert len(parser.sections()) > 0, f"Config {config_path} has no sections"
            except Exception as e:
                pytest.fail(f"Config {config_path} is not valid INI: {e}")
    
    def test_tests_config_has_additional_features(self, root_config_content, tests_config_content):
        """Test that tests config has additional test-specific features"""
        # tests/pytest.ini should have markers since it's in test directory
        assert tests_config_content.has_option('pytest', 'markers'), \
            "tests/pytest.ini should define markers"
        
        # Should have strict-markers in tests config
        tests_addopts = tests_config_content.get('pytest', 'addopts')
        assert '--strict-markers' in tests_addopts, \
            "tests/pytest.ini should enforce strict markers"


@pytest.mark.unit  
class TestConfigurationBestPracticesExtended:
    """Extended best practices tests for pytest configuration"""
    
    def test_config_enables_useful_verbosity(self, root_config_content):
        """Test that verbosity is configured helpfully"""
        addopts = root_config_content.get('pytest', 'addopts')
        
        # Should have at least basic verbosity
        assert '-v' in addopts or '--verbose' in addopts, \
            "Config should enable verbose output for better test feedback"
    
    def test_no_overly_permissive_file_patterns(self, root_config_content):
        """Test that file patterns are not too broad"""
        python_files = root_config_content.get('pytest', 'python_files')
        
        # Should not match all .py files (too broad)
        assert python_files != '*.py', \
            "python_files pattern should not match all .py files (too broad)"
        
        # Should have 'test' in the pattern
        assert 'test' in python_files.lower(), \
            "python_files pattern should include 'test' to avoid collecting non-test files"
    
    def test_function_pattern_prevents_false_matches(self, root_config_content):
        """Test that function pattern doesn't match non-test functions"""
        python_functions = root_config_content.get('pytest', 'python_functions')
        
        # Should start with 'test' to avoid matching helper functions
        assert 'test' in python_functions, \
            "python_functions should include 'test' prefix"
    
    def test_class_pattern_prevents_false_matches(self, root_config_content):
        """Test that class pattern doesn't match non-test classes"""
        python_classes = root_config_content.get('pytest', 'python_classes')
        
        # Should have 'Test' to avoid matching regular classes
        assert 'Test' in python_classes, \
            "python_classes should include 'Test' prefix"
    
    def test_config_prioritizes_explicit_over_implicit(self, root_config_content):
        """Test that config explicitly defines options rather than relying on defaults"""
        required_explicit = ['testpaths', 'python_files', 'python_classes', 'python_functions']
        
        for option in required_explicit:
            assert root_config_content.has_option('pytest', option), \
                f"Config should explicitly define '{option}' rather than relying on defaults"

