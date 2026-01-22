"""
Shared test utilities for workflow tests.

This module provides common helper functions used across workflow test files.
"""


def check_for_hardcoded_secrets(workflow_raw):
    """
    Check for hardcoded secrets in workflow file.
    
    This function detects suspicious patterns that might indicate hardcoded secrets
    while avoiding false positives for legitimate GitHub Actions permission settings.
    
    Args:
        workflow_raw (str): Raw workflow file content
        
    Raises:
        AssertionError: If potential hardcoded secret pattern is found
    """
    suspicious_patterns = ['password', 'token', 'api_key', 'secret']
    lower_content = workflow_raw.lower()
    
    # Valid GitHub Actions permission keys (without colons for flexibility)
    valid_permission_keys = {'id-token', 'contents', 'pages', 'deployments'}
    
    for pattern in suspicious_patterns:
        if pattern not in lower_content:
            continue
            
        lines = workflow_raw.split('\n')
        
        # Identify lines that are inside a top-level 'permissions:' block
        permissions_line_indices = set()
        inside_permissions_block = False
        permissions_indent = None
        
        for idx, raw_line in enumerate(lines):
            stripped = raw_line.lstrip()
            indent = len(raw_line) - len(stripped)
            
            if stripped.startswith('permissions:'):
                inside_permissions_block = True
                permissions_indent = indent
                continue
                
            if inside_permissions_block:
                # Blank lines and comments are still part of the block
                if not stripped or stripped.startswith('#'):
                    permissions_line_indices.add(idx)
                    continue
                    
                # Lines more indented than the 'permissions:' line belong to the block
                if indent > permissions_indent:
                    permissions_line_indices.add(idx)
                else:
                    # We've exited the permissions block
                    inside_permissions_block = False
                    permissions_indent = None
        
        # Check each line for suspicious patterns
        for lineno, line in enumerate(lines):
            if pattern not in line.lower():
                continue
                
            if line.strip().startswith('#'):
                continue
                
            # Skip if this line is part of a permissions block
            if lineno in permissions_line_indices:
                continue
                
            # Skip if it's a valid GitHub Actions permission setting
            # (format-agnostic check for permission keys)
            lower_line = line.lower().strip()
            contains_valid_permission = any(
                lower_line.startswith(key) for key in valid_permission_keys
            )
            if contains_valid_permission:
                continue
                
            # Check if it's using GitHub secrets context or GITHUB_TOKEN
            assert 'secrets.' in line or '${{' in line or 'GITHUB_TOKEN' in line, \
                f"Potential hardcoded secret pattern '{pattern}' found"
