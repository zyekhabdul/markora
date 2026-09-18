#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="markora",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "markora = markora.cli:main",
            "td = markora.cli:main",
        ],
    },
)
