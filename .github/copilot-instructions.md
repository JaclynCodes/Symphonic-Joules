# Copilot Coding Agent Instructions

## Project Overview

Symphonic-Joules is an open-source project that explores the intersection of audio processing and energy calculations. The project harmonizes the worlds of sound and energy through innovative computational approaches, providing tools and insights that bridge the gap between acoustics and physics.

**Key Objectives:**
- Audio analysis and processing of musical compositions and sound waves
- Energy calculations and transformations
- Scientific computing applying physics principles to audio data
- Data visualization for acoustic and energy insights
- Extensible, modular framework for research and development

## Technology Stack

- **Primary Language:** Python
- **Testing Framework:** pytest (configured in `pytest.ini`)
- **Audio Formats:** WAV, MP3, FLAC (standard formats preferred)
- **Documentation:** Markdown

## Repository Structure

```
Symphonic-Joules/
├── .github/          # GitHub workflows and configuration
├── docs/             # Documentation files
├── tests/            # Test files using pytest
├── CONTRIBUTING.md   # Contribution guidelines
├── CHANGELOG.md      # Project changelog
├── LICENSE           # MIT License
└── README.md         # Project overview
```

## Coding Standards

### General Standards
- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names that reflect their purpose
- Write clear comments for complex logic, especially for physics calculations
- Keep functions focused and modular
- Ensure code is well-documented with docstrings

### Testing Requirements
- Write tests for all new features and bug fixes
- Use pytest for all testing (see `pytest.ini` for configuration)
- Tests should be placed in the `tests/` directory
- Follow naming convention: `test_*.py` for test files
- Ensure existing tests continue to pass before submitting changes
- Aim for good test coverage, especially for core functionality

### Documentation Standards
- Update README.md for significant changes to features or usage
- Document new features and APIs with clear explanations
- Include code examples where helpful
- Keep documentation synchronized with code changes
- Update CHANGELOG.md for notable changes

## Domain-Specific Guidelines

### Audio Processing
- Use standard audio formats: WAV, MP3, FLAC
- Always document sampling rates and bit depths in code and tests
- Consider real-time processing requirements in performance-critical code
- Validate audio input/output quality in tests
- Include appropriate error handling for audio file operations

### Energy Calculations
- Use SI units (Joules, Watts) and document unit conversions clearly
- Validate physics calculations with references to scientific literature
- Consider numerical precision and stability in calculations
- Document mathematical formulations with comments or docstrings
- Include uncertainty estimates where applicable

### Scientific Accuracy
- Cite relevant scientific literature in code comments or documentation
- Validate calculations against known physical principles
- Include uncertainty estimates in energy and physics calculations
- Complex calculations should be peer-reviewed through PR process

## Development Workflow

### Branch Strategy
- Create feature branches from main: `feature/your-feature-name`
- Use descriptive branch names that reflect the work being done

### Commit Messages
- Write clear, concise commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issue numbers when applicable

### Pull Request Process
- Provide clear description of changes
- Reference related issues using `#issue-number`
- Ensure all tests pass before requesting review
- Address review comments promptly
- Follow the PR checklist in CONTRIBUTING.md

## Special Instructions

### Files to Handle with Care
- Do not modify `LICENSE` without explicit approval
- Changes to `CONTRIBUTING.md` should align with project maintainer guidelines
- Archive reviews follow the process in `docs/archive-review-process.md`

### Security and Best Practices
- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive configuration
- Validate all external inputs, especially audio files
- Include appropriate error handling and logging

### Code Review Requirements
- All PRs require at least one review before merging
- Focus on constructive feedback during reviews
- Maintain a positive, collaborative environment
- Test changes locally before pushing

## Getting Help

- Check existing documentation in `docs/` directory
- Review CONTRIBUTING.md for detailed contribution guidelines
- Ask questions in GitHub Issues or Discussions
- Reference the README.md for project overview and goals

## Acceptance Criteria for Tasks

When completing assigned tasks, ensure:
- [ ] Code follows project style guidelines and PEP 8
- [ ] All new code includes appropriate tests
- [ ] Tests pass locally using pytest
- [ ] Documentation is updated for user-facing changes
- [ ] Commit messages are clear and descriptive
- [ ] Changes are focused and atomic
- [ ] Related issues are referenced in PR description
- [ ] No secrets or sensitive data are committed
- [ ] Audio files use standard formats with documented parameters
- [ ] Physics calculations are validated and documented
