#!/usr/bin/env python3
"""
Monster Battle - Setup and Installation Script
Installs required dependencies and checks system compatibility
"""

import sys
import subprocess
import platform
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python 3.6 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_module_installed(module_name):
    """Check if a module is installed"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def install_pygame():
    """Install pygame using pip"""
    print("Installing pygame...")
    
    try:
        # First try to upgrade pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        print("✅ pip upgraded successfully")
    except subprocess.CalledProcessError:
        print("⚠️ Could not upgrade pip, continuing anyway...")
    
    try:
        # Install pygame
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'pygame'], 
                               check=True, capture_output=True, text=True)
        print("✅ pygame installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install pygame: {e}")
        print("Error output:", e.stderr)
        return False

def test_pygame():
    """Test if pygame works correctly"""
    try:
        import pygame
        pygame.init()
        print(f"✅ pygame {pygame.version.ver} is working correctly!")
        
        # Test basic functionality
        display = pygame.display.set_mode((100, 100))
        pygame.display.quit()
        print("✅ pygame display test passed!")
        return True
        
    except Exception as e:
        print(f"❌ pygame test failed: {e}")
        return False

def main():
    print("=" * 50)
    print("🎮 Monster Battle - Setup & Installation")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python_version():
        print("\nPlease install Python 3.6 or higher from: https://www.python.org/downloads/")
        input("Press Enter to exit...")
        return False
    
    print(f"Platform: {platform.system()} {platform.release()}")
    print()
    
    # Check if pygame is already installed
    if check_module_installed('pygame'):
        print("✅ pygame is already installed")
        if test_pygame():
            print("\n🎉 All dependencies are working!")
            print("You can now run Monster Battle!")
        else:
            print("\n❌ pygame is installed but not working correctly")
            print("Try reinstalling pygame manually")
        
    else:
        print("❌ pygame is not installed")
        print("Attempting to install pygame...")
        print()
        
        if install_pygame():
            print("\nTesting pygame installation...")
            if test_pygame():
                print("\n🎉 Setup completed successfully!")
                print("You can now run Monster Battle!")
            else:
                print("\n❌ pygame was installed but is not working correctly")
                return False
        else:
            print("\n❌ Failed to install pygame")
            print("\nManual installation steps:")
            print("1. Open terminal/command prompt")
            print("2. Run: python -m pip install pygame")
            print("3. If that fails, try: python -m pip install --user pygame")
            return False
    
    print("\n" + "=" * 50)
    print("🚀 How to play Monster Battle:")
    print("=" * 50)
    print("📱 Network Multiplayer:")
    print("  1. Host: Run start_game.bat → Option 1 (Start Server)")
    print("  2. Guest: Run start_game.bat → Option 2 (Join Game)")
    print()
    print("🖥️  Local Play:")
    print("  - Run start_game.bat → Option 6 (Local Game)")
    print()
    print("🔧 Troubleshooting:")
    print("  - Run start_game.bat → Option 4 (Network Diagnostics)")
    print()
    
    input("Press Enter to exit...")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        input("Press Enter to exit...")