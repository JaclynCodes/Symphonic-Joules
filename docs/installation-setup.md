# Installation and Setup for Symphonic-Joules

## Quick Start

**For developers wanting to get started immediately:**

```bash
# Clone, setup, and test
git clone https://github.com/JaclynCodes/Symphonic-Joules.git
cd Symphonic-Joules
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r tests/requirements.txt  # Install test dependencies
pytest
```

Continue reading for detailed information about installation methods and troubleshooting.

---

## Important Note

This document addresses the installation and setup process for **Symphonic-Joules**, a project focused on audio processing and energy calculations.

**Note**: If you were looking for darktable (photography workflow application) installer information, you may have reached this repository in error. Darktable has its own repository at https://github.com/darktable-org/darktable.

## Current Status

Symphonic-Joules is currently in early development. The project does not yet have:
- A Windows installer package
- Binary distributions
- Formal packaging infrastructure
- Deployment scripts

## Installation Methods

### For Developers (Current)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/JaclynCodes/Symphonic-Joules.git
   cd Symphonic-Joules
   ```

2. **Set Up Python Environment**
   ```bash
   # Create virtual environment (recommended)
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```
   
   **Note for macOS users**: If you experience compatibility issues, see the [Python Version Compatibility](#macos-python-version-compatibility) section below for information about using Python 3.11.

3. **Install Dependencies**
   ```bash
   # Dependencies will be specified as the project develops
   # pip install -r requirements.txt (when available)
   ```

4. **Run Tests**
   ```bash
   pytest
   ```

## Future Packaging Plans

As the project matures, the following packaging and installation methods may be implemented:

### Potential Installation Methods

1. **PyPI Package** (Python Package Index)
   - Standard Python package installation
   - `pip install symphonic-joules`
   - Cross-platform support

2. **Conda Package**
   - Conda-forge distribution
   - `conda install -c conda-forge symphonic-joules`
   - Simplified dependency management

3. **Platform-Specific Installers** (Future Consideration)
   - Windows: MSI installer or standalone executable
   - macOS: DMG or Homebrew formula
   - Linux: DEB/RPM packages or AppImage

4. **Portable Distributions**
   - Standalone executables with bundled dependencies
   - No installation required

## Installation Requirements

### System Requirements (Projected)

- **Operating Systems**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python Version**: 3.8 or higher (Python 3.11 recommended for macOS users experiencing compatibility issues)
- **Audio Hardware**: Standard audio input/output capabilities
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: Varies based on audio file processing needs

### Python Dependencies (To Be Determined)

Common dependencies for audio processing and scientific computing:
- NumPy - Numerical computing
- SciPy - Scientific computing
- Audio libraries (librosa, pydub, or similar)
- Matplotlib/Plotly - Data visualization
- pytest - Testing framework

## Configuration

Configuration options and settings will be documented as features are implemented.

### Planned Configuration Areas

1. **Audio Processing**
   - Sample rates
   - Bit depths
   - Audio formats
   - Buffer sizes

2. **Energy Calculations**
   - Unit preferences
   - Precision settings
   - Calculation methods

3. **Performance**
   - Multi-threading options
   - Memory limits
   - Cache settings

## Deployment Scenarios

### Development Installation
- Git clone and virtual environment setup
- Editable install for development
- Access to test suite and examples

### User Installation (Future)
- Package manager installation
- Pre-built binaries
- Simplified setup process

### Enterprise/Research Deployment (Future)
- Silent installation options
- Configuration file deployment
- Centralized updates
- Custom installation paths

## Troubleshooting

### Common Issues

**Issue**: Unable to process audio files
- **Solution**: Ensure audio libraries are properly installed and audio files are in supported formats

**Issue**: Import errors
- **Solution**: Verify all dependencies are installed in the active Python environment

**Issue**: Performance issues with large audio files
- **Solution**: Check available memory, consider processing in chunks

### Platform-Specific Issues

#### macOS: Python Version Compatibility

Some macOS users may experience compatibility issues with newer Python versions (3.12+). If you encounter such issues, you can use Python 3.11 as a temporary workaround:

**Temporary fix with downgrading Python on macOS:**

1. Install Python 3.11 using Homebrew:
   ```bash
   brew install python@3.11
   ```

2. Add Python 3.11 to your PATH by adding this line to your `~/.zshrc` file:
   ```bash
   export PATH="/opt/homebrew/opt/python@3.11/libexec/bin:$PATH"
   ```

3. Reload your shell configuration:
   ```bash
   source ~/.zshrc
   ```

4. Verify the Python version:
   ```bash
   python --version
   ```

**Note**: This is a temporary workaround. The project aims to support the latest stable Python versions. Check the project's GitHub issues for updates on Python version compatibility.

## Getting Help

- **Documentation**: See the [docs](.) directory
- **Issues**: Report issues at [GitHub Issues](https://github.com/JaclynCodes/Symphonic-Joules/issues)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## Roadmap for Installation Infrastructure

- [ ] Define core dependencies
- [ ] Create `requirements.txt` and `setup.py`
- [ ] Set up PyPI package structure
- [ ] Create automated build scripts
- [ ] Develop platform-specific installers (if needed)
- [ ] Document installation procedures
- [ ] Create troubleshooting guides
- [ ] Set up continuous integration for packaging

## References

- [Python Packaging Guide](https://packaging.python.org/)
- [Conda Package Building](https://docs.conda.io/projects/conda-build/en/latest/)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/) (for standalone executables)

---

*This document will be updated as the project's installation and packaging infrastructure develops.*
