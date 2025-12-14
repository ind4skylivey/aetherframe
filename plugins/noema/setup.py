"""
Noema - Intent Classification Plugin for AetherFrame

Infers malicious intent from behavioral patterns and API usage.
"""
from setuptools import setup, find_packages

setup(
    name="aetherframe-noema",
    version="0.1.0",
    description="Intent classification plugin for AetherFrame",
    author="ind4skylivey",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.11",
    entry_points={
        "aetherframe.plugins": [
            "noema=noema.plugin:NoemaPlugin",
        ],
    },
)
