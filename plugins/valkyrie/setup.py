"""
Valkyrie - Binary Validation Plugin for AetherFrame

Validates binary integrity and performs initial triage.
"""
from setuptools import setup, find_packages

setup(
    name="aetherframe-valkyrie",
    version="0.1.0",
    description="Binary validation plugin for AetherFrame",
    author="ind4skylivey",
    packages=find_packages(),
    install_requires=[
        "pefile>=2023.2.7",
    ],
    python_requires=">=3.11",
    entry_points={
        "aetherframe.plugins": [
            "valkyrie=valkyrie.plugin:ValkyriePlugin",
        ],
    },
)
