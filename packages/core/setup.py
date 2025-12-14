from setuptools import setup, find_packages

setup(
    name="aetherframe-core",
    version="0.1.0",
    description="AetherFrame Core - Malware Analysis Backend",
    packages=find_packages(),
    install_requires=[
        # Will be populated from requirements.txt
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
    },
    python_requires=">=3.11",
)
