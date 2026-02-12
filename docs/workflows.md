# GitHub Workflows

This document describes the GitHub Actions workflows used in the Symphonic-Joules project.

## Available Workflows

### Update Dependencies

**File:** `.github/workflows/update_dependencies.yml`

**Purpose:** Automates checking and updating Python package dependencies.

**Triggers:**
- **Schedule:** Runs automatically every Monday at 9:00 AM UTC
- **Manual:** Can be triggered manually via GitHub Actions UI

**Environment Variables:**
- `PYTHON_VERSION`: The Python version used for updates (default: 3.11)
- `PIP_VERSION`: The pip version used (default: 24.0)

**Manual Trigger Options:**
- `package`: Specify a particular package to update (e.g., `numpy`, `librosa`)
- `version`: Specify the target version for the package (leave empty for latest)

**What It Does:**
1. Checks out the repository
2. Sets up Python environment with configured version
3. Installs current dependencies
4. Checks for outdated packages
5. (Optional) Updates specific package if provided
6. Creates a new branch with updates
7. Commits and pushes changes

**Usage Examples:**

**Check all packages for updates:**
- Go to Actions tab
- Select "Update Dependencies" workflow
- Click "Run workflow"
- Leave inputs empty
- Click "Run workflow"

**Update specific package:**
- Go to Actions tab
- Select "Update Dependencies" workflow
- Click "Run workflow"
- Enter package name (e.g., `numpy`)
- Optionally enter version (e.g., `1.24.0`)
- Click "Run workflow"

**Notes:**
- The workflow only runs if the repository owner is `JaclynCodes`
- Changes are pushed to a new branch with format `automated/update-dependencies-YYYYMMDD`
- Manual review is recommended before merging dependency updates
- The workflow uses GitHub Actions bot for commits

## Other Workflows

### CI (Continuous Integration)
**File:** `.github/workflows/blank.yml`
- Runs on push and pull requests to main branch
- Performs linting, testing, and builds

### CodeQL Advanced
**File:** `.github/workflows/codeql.yml`
- Security scanning workflow
- Runs on schedule and PR events

### License Check
**File:** `.github/workflows/license-check.yml`
- Validates license compliance

### Static Content Deployment
**File:** `.github/workflows/static.yml`
- Deploys static content to GitHub Pages

## Contributing

When adding or modifying workflows:
1. Follow YAML best practices
2. Use environment variables for configuration
3. Add appropriate documentation
4. Test workflows before merging
5. Follow the repository's contribution guidelines
