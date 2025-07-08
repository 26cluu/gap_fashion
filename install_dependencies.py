#!/usr/bin/env python3
"""
Installation script for Fashion Analysis Tool dependencies.
This script handles dependency installation with better error handling.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def install_package(package, description=None):
    """Install a single package with error handling."""
    if description is None:
        description = f"Installing {package}"

    return run_command(f"pip install {package}", description)


def main():
    """Main installation function."""
    print("Fashion Analysis Tool - Dependency Installer")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False

    print(
        f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected"
    )

    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("Warning: Failed to upgrade pip, continuing anyway...")

    # Install packages one by one to handle errors individually
    packages = [
        ("numpy>=1.24.0", "Installing NumPy"),
        ("Pillow>=10.0.0", "Installing Pillow"),
        ("requests>=2.31.0", "Installing Requests"),
        ("matplotlib>=3.7.0", "Installing Matplotlib"),
    ]

    for package, description in packages:
        if not install_package(package, description):
            print(f"Failed to install {package}")
            return False

    # Install PyTorch with specific command for Windows
    print("\nInstalling PyTorch...")
    torch_command = (
        "pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu"
    )
    if not run_command(torch_command, "Installing PyTorch (CPU version)"):
        print("Trying alternative PyTorch installation...")
        if not run_command(
            "pip install torch torchvision", "Installing PyTorch (alternative method)"
        ):
            print("Failed to install PyTorch")
            return False

    # Install transformers
    if not install_package("transformers>=4.30.0", "Installing Transformers"):
        print("Failed to install Transformers")
        return False

    # Verify installation
    print("\nVerifying installation...")
    verification_code = """
import torch
import transformers
import matplotlib
import PIL
import numpy
import requests
print("✓ All dependencies installed successfully!")
print(f"PyTorch version: {torch.__version__}")
print(f"Transformers version: {transformers.__version__}")
"""

    try:
        result = subprocess.run(
            [sys.executable, "-c", verification_code],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Verification failed:")
        print(e.stderr)
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Installation completed successfully!")
        print("You can now run the fashion analysis tool.")
    else:
        print("\n❌ Installation failed. Please check the error messages above.")
        print("\nAlternative installation methods:")
        print("1. Try installing Microsoft Visual C++ Build Tools:")
        print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print("2. Use conda instead of pip:")
        print(
            "   conda install pytorch torchvision transformers matplotlib pillow numpy requests -c pytorch"
        )
        print(
            "3. Try installing packages individually to identify the problematic one."
        )

    input("\nPress Enter to exit...")
