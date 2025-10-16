#!/usr/bin/env python3
"""
Setup script for Brightface Content Engine
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_environment():
    """Set up the environment for the content engine"""
    print("Setting up Brightface Content Engine...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        sys.exit(1)
    
    # Create necessary directories
    directories = ["logs", "data", "credentials"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Check for environment file
    if not os.path.exists(".env"):
        if os.path.exists("env.example"):
            print("Creating .env file from template...")
            with open("env.example", "r") as src:
                with open(".env", "w") as dst:
                    dst.write(src.read())
            print("✓ Created .env file from template")
        else:
            print("⚠ No .env file found. Please create one with your API keys.")
    
    # Check for Google credentials
    if not os.path.exists("credentials.json"):
        print("⚠ Google credentials.json not found. Please add your Google API credentials.")
    
    print("\nSetup complete! Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Add Google credentials.json file")
    print("3. Run: python qa_tester.py to test the system")
    print("4. Run: python main.py to start the content engine")

def validate_setup():
    """Validate the setup"""
    print("Validating setup...")
    
    # Check required files
    required_files = ["config.py", "models.py", "main.py", "requirements.txt"]
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} missing")
            return False
    
    # Check environment variables
    try:
        from config import Config
        if Config.validate():
            print("✓ Configuration validation passed")
        else:
            print("✗ Configuration validation failed")
            return False
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    print("✓ Setup validation passed")
    return True

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        validate_setup()
    else:
        setup_environment()

if __name__ == "__main__":
    main()
