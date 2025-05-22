#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="smartnoteparser",
    version="0.1.0",
    author="Anonymous",
    author_email="noreply@example.com",
    description="A simple CLI tool to parse notes and extract structured information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/smartnoteparser",
    py_modules=["main", "parser", "exporter"],
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "smartnoteparser=main:parse_notes",
        ],
    },
)