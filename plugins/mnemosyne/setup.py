"""
Mnemosyne - State Reconstruction Plugin for AetherFrame

Reconstructs program state from memory dumps and trace data.
"""
from setuptools import setup, find_packages

setup(
    name="aetherframe-mnemosyne",
    version="0.1.0",
    description="State reconstruction plugin for AetherFrame",
    author="ind4skylivey",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.11",
    entry_points={
        "aetherframe.plugins": [
            "mnemosyne=mnemosyne.plugin:MnemosynePlugin",
        ],
    },
)
