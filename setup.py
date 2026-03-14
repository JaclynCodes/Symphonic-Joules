"""Setup script for Symphonic-Joules package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="symphonic-joules",
    version="0.1.0",
    author="JaclynCodes",
    description="A project that harmonizes the worlds of sound and energy through innovative computational approaches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JaclynCodes/Symphonic-Joules",
    project_urls={
        "Bug Tracker": "https://github.com/JaclynCodes/Symphonic-Joules/issues",
        "Documentation": "https://github.com/JaclynCodes/Symphonic-Joules/tree/main/docs",
        "Source Code": "https://github.com/JaclynCodes/Symphonic-Joules",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-xdist>=3.0.0",  # Parallel test execution
            "PyYAML>=5.1",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
