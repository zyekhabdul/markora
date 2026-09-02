#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="td-notes",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "td = td.cli:main",
            "todo = td.cli:main",
        ],
    },
)
