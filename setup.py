"""
Rodent AI Vision Box
A professional-grade AI-powered rodent detection system using computer vision.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="rodent-ai-vision-box",
    version="1.0.0",
    author="AI Vision Systems",
    author_email="support@aivisionsystems.com",
    description="AI-powered rodent detection system for real-time monitoring and alerts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rodent-ai-vision-box",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/rodent-ai-vision-box/issues",
        "Documentation": "https://github.com/yourusername/rodent-ai-vision-box/wiki",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    packages=find_packages(exclude=["tests*", "docs*", "dataset*", "colab*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rodent-detect=src.main:main",
            "rodent-test-twilio=test_twilio:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.onnx"],
    },
    zip_safe=False,
)