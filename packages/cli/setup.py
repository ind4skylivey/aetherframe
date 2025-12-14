from setuptools import setup, find_packages

setup(
    name="aetherframe-cli",
    version="0.1.0",
    description="AetherFrame Command Line Interface",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "aetherframe=reveris.main:cli",
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "rich>=13.0.0",
    ],
    python_requires=">=3.11",
)
