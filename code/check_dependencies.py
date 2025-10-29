#!/usr/bin/env python3
"""
Check if all required dependencies are installed before running the game
"""

import sys
import importlib.util

def check_dependency(module_name, install_name=None):
    """Check if a module is available"""
    if install_name is None:
        install_name = module_name
        
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ Missing dependency: {module_name}")
        print(f"   Install with: python -m pip install {install_name}")
        return False
    else:
        print(f"✅ {module_name} is available")
        return True

def main():
    print("Checking Monster Battle dependencies...")
    print()
    
    dependencies_ok = True
    
    # Check Python version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print(f"❌ Python 3.6+ required, found {version.major}.{version.minor}")
        dependencies_ok = False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    # Check required modules
    required_modules = [
        ('pygame', 'pygame'),
    ]
    
    for module, install_name in required_modules:
        if not check_dependency(module, install_name):
            dependencies_ok = False
    
    print()
    
    if dependencies_ok:
        print("🎉 All dependencies are satisfied!")
        return True
    else:
        print("❌ Some dependencies are missing!")
        print()
        print("To install missing dependencies:")
        print("1. Run setup.bat (Windows) or setup.py (Cross-platform)")
        print("2. Or manually: python -m pip install pygame")
        print()
        return False

if __name__ == "__main__":
    if not main():
        input("Press Enter to exit...")
        sys.exit(1)