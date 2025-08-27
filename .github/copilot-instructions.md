# Symphonic-Joules GitHub Copilot Instructions

**ALWAYS follow these instructions first and only fallback to additional search and context gathering if the information here is incomplete or found to be in error.**

Symphonic-Joules is an open-source project exploring the intersection of audio processing and energy calculations. The project is currently in **early development phase** with comprehensive documentation but minimal implementation.

## Project Status & Working Effectively

### Current State (CRITICAL - Read First)
- **No source code implementation yet** - This is a documentation-first project in early development
- **No build system exists** - There are no build scripts, package.json, requirements.txt, or Makefile
- **No test infrastructure** - No test files or testing framework is implemented
- **Documentation-heavy structure** - Extensive documentation exists in `docs/` directory
- **Basic GitHub Actions** - Only a placeholder workflow (`.github/workflows/blank.yml`) that prints "Hello, world!"

### Available Tools & Environment
- **Python 3.12.3** - Available and working
- **Node.js v20.19.4** - Available and working  
- **npm 10.8.2** - Available and working
- **pip3 24.0** - Available and working
- **Git** - Fully functional

### DO NOT attempt these commands (they will fail):
- `npm install` - No package.json exists
- `pip install -r requirements.txt` - No requirements.txt exists
- `python setup.py install` - No setup.py exists
- `make` or `make test` - No Makefile exists
- `cargo build` - Not a Rust project
- `mvn install` - Not a Maven project

### Working with the Current Repository

#### Repository Navigation
```bash
# Navigate to repository root
cd /home/runner/work/Symphonic-Joules/Symphonic-Joules

# View repository structure
ls -la

# Explore documentation
find docs/ -name "*.md" | sort
```

#### Available Documentation Files
- `README.md` - Project overview and roadmap
- `CONTRIBUTING.md` - Contribution guidelines
- `docs/getting-started.md` - Getting started guide
- `docs/architecture.md` - Planned system architecture
- `docs/api-reference.md` - Future API documentation
- `docs/faq.md` - Frequently asked questions
- `docs/examples/README.md` - Examples framework (no actual examples yet)
- `github-copilot-setup.md` - GitHub Copilot setup guide

#### GitHub Actions Workflow
```bash
# The only working "build" command currently available:
echo "Hello, world!"
echo "Add other actions to build,"
echo "test, and deploy your project."

# View the workflow file:
cat .github/workflows/blank.yml
```

## Development Guidelines

### When Implementation Begins
Once actual source code is added to this repository:

1. **Determine Tech Stack**: Check for package.json, requirements.txt, or other config files
2. **Install Dependencies**: Use appropriate package manager (npm, pip, etc.)
3. **Set Up Development Environment**: Follow language-specific setup
4. **Implement Build System**: Add build scripts and test infrastructure
5. **Update These Instructions**: Modify this file with working commands

### Future Build & Test Expectations
When development progresses, expect these patterns:

#### For Python Projects:
```bash
# Typical Python setup (not yet applicable)
pip3 install -r requirements.txt
python -m pytest tests/
python -m flake8 src/
python -m black src/
```

#### For Node.js Projects:
```bash
# Typical Node.js setup (not yet applicable)
npm install
npm test
npm run lint
npm run build
```

#### For Audio Processing Projects:
- **NEVER CANCEL**: Audio processing builds can take 30+ minutes. Set timeout to 60+ minutes.
- **Dependencies**: May require system-level audio libraries (FFMPEG, SoX, etc.)
- **Testing**: Audio tests may require sample files and longer validation

### Contributing to Documentation

#### Always Safe Commands:
```bash
# These commands always work and are safe:
git status
git log --oneline -10
ls -la docs/
cat README.md
find . -name "*.md" -type f
```

#### Documentation Updates:
When contributing to documentation:
1. **Update relevant .md files** in docs/ directory
2. **Maintain consistency** with existing documentation structure
3. **No build step required** - Documentation changes need no compilation
4. **Test links** manually by checking referenced files exist

## Validation & Testing

### Current Validation (What Actually Works):
```bash
# Repository exploration
ls -la
find docs/ -type f -name "*.md"
cat docs/README.md

# Git operations
git status
git log --oneline -5

# Basic tool verification
python3 --version
node --version
npm --version
pip3 --version

# Documentation validation
grep -r "TODO" docs/ || echo "No TODOs found"
find . -name "*.md" -exec wc -l {} \; | sort -n
```

### Future Validation (When Code Exists):
When source code is implemented, always run:
1. **Full build process** - May take 45+ minutes. NEVER CANCEL. Set timeout to 90+ minutes.
2. **Complete test suite** - May take 15+ minutes. NEVER CANCEL. Set timeout to 30+ minutes.
3. **Linting and formatting** - Usually quick, under 2 minutes
4. **Documentation generation** - If applicable

## Project-Specific Knowledge

### Core Concepts:
- **Symphonic**: Structured, harmonic nature of music and sound
- **Joules**: Fundamental unit of energy in physics
- **Goal**: Bridge audio processing and energy calculations
- **Approach**: Modular framework with scientific accuracy

### Key Documentation Sections:
- Architecture focuses on modularity and scientific accuracy
- API reference shows planned Python-style interfaces
- Examples directory prepared for future code samples
- FAQ addresses common questions about early development stage

### Common File Locations:
```
Symphonic-Joules/
├── .github/workflows/    # GitHub Actions (basic placeholder)
├── docs/                 # Comprehensive documentation
│   ├── api-reference.md  # Future API documentation
│   ├── architecture.md   # System design
│   ├── examples/         # Future code examples
│   ├── faq.md           # Frequently asked questions
│   └── getting-started.md # Installation guide
├── CONTRIBUTING.md       # Contribution guidelines
├── README.md            # Project overview
└── github-copilot-setup.md # Copilot setup guide
```

## Timeouts & Performance Expectations

### Current Commands (All < 5 seconds):
- Documentation viewing: Instant
- Git operations: < 2 seconds
- File system operations: < 1 second
- Tool version checks: < 2 seconds

### Future Implementation Expectations:
- **Audio processing builds**: 30-60 minutes. NEVER CANCEL. Set timeout to 90+ minutes.
- **Scientific computing setup**: 15-30 minutes. NEVER CANCEL. Set timeout to 45+ minutes.
- **Test suites with audio**: 10-20 minutes. NEVER CANCEL. Set timeout to 30+ minutes.
- **Dependency installation**: 5-15 minutes depending on audio libraries

## Error Handling & Troubleshooting

### Common Current Issues:
- **"No such file or directory" for source files**: Expected - no implementation yet
- **"Command not found" for build tools**: Expected - no build system implemented
- **Missing package files**: Expected - dependencies not defined yet

### Reporting Issues:
When actual implementation begins and you encounter problems:
1. Check if the issue is related to missing implementation (expected)
2. Verify tool availability (Python, Node.js versions)
3. Document specific error messages and context
4. Include system information if relevant

## References for Implementation

### Existing Documentation to Consult:
- `docs/architecture.md` - Planned system design
- `docs/api-reference.md` - Expected API structure
- `CONTRIBUTING.md` - Development guidelines
- `docs/faq.md` - Common questions and answers

### When Code is Added:
Always update this file with:
- Working build commands
- Actual test procedures
- Real timeout values from testing
- Specific dependency requirements
- Validated installation steps

---

**Remember**: This project is documentation-heavy and implementation-light. Focus on documentation consistency and preparation for future development rather than trying to build or test non-existent code.