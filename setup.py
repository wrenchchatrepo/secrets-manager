"""
Setup script for the secrets-manager package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="secrets-manager",
    version="0.1.0",
    author="Dion Edge",
    author_email="dion@wrench.chat",
    description="Secure Credential Management System for macOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wrenchchatrepo/secrets-manager",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "secrets-manager=secrets_manager.cli:main",
            "secrets-manager-server=secrets_manager.server:main",
        ],
    },
) 