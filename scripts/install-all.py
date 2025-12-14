#!/usr/bin/env python3
"""Install all AetherFrame packages in development mode."""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def install_package(package_path, package_type="python"):
    """Install a single package."""
    print(f"\n📦 Installing {package_path.name}...")

    try:
        if package_type == "python":
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."],
                cwd=package_path,
                check=True
            )
        elif package_type == "node":
            subprocess.run(
                ["npm", "install"],
                cwd=package_path,
                check=True
            )
        print(f"✅ {package_path.name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_path.name}: {e}")
        return False

def main():
    print("🚀 Installing AetherFrame Ecosystem - All Packages\n")

    # Python packages
    python_packages = [
        REPO_ROOT / "packages/core",
        REPO_ROOT / "packages/cli",
        REPO_ROOT / "plugins/umbriel",
        # Add more plugins as they're created
    ]

    # Node packages
    node_packages = [
        REPO_ROOT / "packages/frontend",
    ]

    success_count = 0
    total_count = len(python_packages) + len(node_packages)

    # Install Python packages
    for pkg in python_packages:
        if pkg.exists():
            if install_package(pkg, "python"):
                success_count += 1

    # Install Node packages
    for pkg in node_packages:
        if pkg.exists():
            if install_package(pkg, "node"):
                success_count += 1

    print(f"\n{'='*50}")
    print(f"Installation complete: {success_count}/{total_count} packages")
    print(f"{'='*50}")

    if success_count == total_count:
        print("\n✅ All packages installed successfully!")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count} package(s) failed to install")
        return 1

if __name__ == "__main__":
    sys.exit(main())
