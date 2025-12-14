"""
Umbriel - Anti-Analysis Detection Plugin for AetherFrame

Detects anti-debugging, anti-VM, anti-instrumentation, and obfuscation techniques.
"""
from setuptools import setup, find_packages

setup(
    name="aetherframe-umbriel",
    version="0.1.0",
    description="Anti-analysis detection plugin for AetherFrame",
    author="ind4skylivey",
    packages=find_packages(),
    install_requires=[
        "pefile>=2023.2.7",
        "capstone>=5.0.0",
    ],
    python_requires=">=3.11",
    entry_points={
        "aetherframe.plugins": [
            "umbriel=umbriel.plugin:UmbrielPlugin",
        ],
    },
)
